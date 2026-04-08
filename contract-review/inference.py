#!/usr/bin/env python3
"""
Baseline inference script for the Contract Review RL Environment.

This script runs an LLM agent against all 3 tasks and logs results
in the required [START] / [STEP] / [END] format for automated evaluation.

Required environment variables:
    API_BASE_URL  - LLM API endpoint  (e.g. https://api-inference.huggingface.co/v1)
    MODEL_NAME    - Model identifier   (e.g. meta-llama/Llama-3.3-70B-Instruct)
    HF_TOKEN      - HuggingFace / API key
    SPACE_URL     - Environment URL    (e.g. https://YOUR_USER-contract-review-env.hf.space)
                    Defaults to http://localhost:7860 for local testing.

Usage:
    export API_BASE_URL="https://api-inference.huggingface.co/v1"
    export MODEL_NAME="meta-llama/Llama-3.3-70B-Instruct"
    export HF_TOKEN="hf_..."
    export SPACE_URL="https://YOUR_USER-contract-review-env.hf.space"
    python inference.py
"""

import os
import sys
import json
import time
import requests
from typing import List, Optional
from openai import OpenAI

# â”€â”€ Configuration â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

API_BASE_URL: str = os.environ.get("API_BASE_URL", "https://api-inference.huggingface.co/v1")
MODEL_NAME: str   = os.environ.get("MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct")
HF_TOKEN: str     = os.environ.get("HF_TOKEN", "")
SPACE_URL: str    = os.environ.get("SPACE_URL", "http://localhost:7860").rstrip("/")

BENCHMARK          = "contract-review-env"
TASKS              = ["easy", "medium", "hard"]
MAX_STEPS          = 3        # max steps per task episode
MAX_TOTAL_REWARD   = 3.0      # 3 steps Ã— 1.0 max reward each
SUCCESS_THRESHOLD  = 0.60     # score >= 0.60 = success


# â”€â”€ Required log functions (DO NOT CHANGE FORMAT) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def log_start(task: str, env: str, model: str) -> None:
    print("[START]", json.dumps({
        "task": task,
        "env": env,
        "model": model,
    }), flush=True)


def log_step(step: int, action: str, reward: float, done: bool,
             error: Optional[str]) -> None:
    print("[STEP]", json.dumps({
        "step": step,
        "action": action,
        "reward": round(reward, 4),
        "done": done,
        "error": error,
    }), flush=True)


def log_end(success: bool, steps: int, score: float,
            rewards: List[float]) -> None:
    print("[END]", json.dumps({
        "success": success,
        "steps": steps,
        "score": round(score, 4),
        "rewards": [round(r, 4) for r in rewards],
    }), flush=True)


# â”€â”€ Lightweight HTTP environment client â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class EnvClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def reset(self, task_id: str = "easy") -> dict:
        r = requests.post(
            f"{self.base_url}/reset",
            json={"task_id": task_id},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def step(self, action: dict) -> dict:
        r = requests.post(
            f"{self.base_url}/step",
            json={"action": action},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()


# â”€â”€ LLM agent â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

SYSTEM_PROMPT = """You are an expert legal contract reviewer with 20+ years of experience.

Your job: review the given contract(s) and return ONLY a valid JSON object with this structure:
{
  "risk_level": "low" | "medium" | "high",
  "missing_clauses": ["list of missing standard clause names"],
  "contradictions": ["list of conflicts found between documents"],
  "flagged_language": ["specific problematic phrases from the contract"],
  "review_notes": "detailed explanation of all issues found"
}

Rules:
- Respond with ONLY the JSON object. No preamble, no explanation outside the JSON.
- risk_level must be exactly "low", "medium", or "high".
- missing_clauses: use standard legal names (e.g. "indemnification", "limitation of liability").
- contradictions: only for cross-document conflicts (leave empty if single document).
- review_notes: be specific â€” quote the problematic language and explain the risk.
"""


def get_agent_action(
    openai_client: OpenAI,
    contract_text: str,
    task_description: str,
    feedback: str = "",
    hints: List[str] = [],
    history: List[dict] = [],
    step: int = 1,
) -> dict:
    """Call the LLM and parse its JSON response into a contract review action."""

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Include recent history for multi-step refinement
    for turn in history[-4:]:
        messages.append(turn)

    # Build the user message
    user_parts = [
        f"TASK INSTRUCTIONS:\n{task_description}",
        f"\nCONTRACT TEXT:\n{contract_text}",
    ]

    if feedback and step > 1:
        user_parts.append(f"\nFEEDBACK FROM PREVIOUS ATTEMPT:\n{feedback}")

    if hints:
        user_parts.append(
            "\nHINTS (incorporate these into your improved review):\n"
            + "\n".join(f"  â€¢ {h}" for h in hints)
        )

    if step > 1:
        user_parts.append(
            f"\nThis is review attempt {step} of {MAX_STEPS}. "
            "Improve your answer using the feedback and hints above."
        )

    messages.append({"role": "user", "content": "\n".join(user_parts)})

    try:
        response = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=900,
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if present
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        action = json.loads(raw)

        # Ensure all required fields exist
        action.setdefault("risk_level", "medium")
        action.setdefault("missing_clauses", [])
        action.setdefault("contradictions", [])
        action.setdefault("flagged_language", [])
        action.setdefault("review_notes", "")

        return action

    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON parse error at step {step}: {e}", flush=True)
        return {
            "risk_level": "medium",
            "missing_clauses": [],
            "contradictions": [],
            "flagged_language": [],
            "review_notes": f"Parse error: {e}. Raw: {raw[:200]}",
        }
    except Exception as e:
        print(f"[DEBUG] LLM call error: {e}", flush=True)
        return {
            "risk_level": "medium",
            "missing_clauses": [],
            "contradictions": [],
            "flagged_language": [],
            "review_notes": f"Error: {e}",
        }


# â”€â”€ Single task runner â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def run_task(env: EnvClient, openai_client: OpenAI, task_id: str) -> dict:
    """
    Run one full episode for a task.
    Logs [START], [STEP]Ã—N, [END] and returns result summary.
    """
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    history: List[dict] = []
    last_feedback = ""
    last_hints: List[str] = []

    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

    try:
        # Reset environment
        result = env.reset(task_id=task_id)
        obs = result["observation"]

        for step in range(1, MAX_STEPS + 1):
            if result.get("done", False):
                break

            # Get LLM action
            action = get_agent_action(
                openai_client=openai_client,
                contract_text=obs["contract_text"],
                task_description=obs["task_description"],
                feedback=last_feedback,
                hints=last_hints,
                history=history,
                step=step,
            )

            # Compact action string for log (truncated)
            action_log = json.dumps({
                "risk_level": action.get("risk_level"),
                "missing_clauses": action.get("missing_clauses", []),
                "contradictions": action.get("contradictions", []),
            })[:300]

            # Step environment
            result = env.step(action)
            obs = result["observation"]
            reward = float(result.get("reward", 0.0))
            done = bool(result.get("done", False))

            rewards.append(reward)
            steps_taken = step
            last_feedback = obs.get("feedback", "")
            last_hints = obs.get("hints", [])

            # Add to conversation history for next step
            history.append({"role": "assistant", "content": json.dumps(action)})
            history.append({
                "role": "user",
                "content": f"Feedback from grader: {last_feedback}"
            })

            log_step(
                step=step,
                action=action_log,
                reward=reward,
                done=done,
                error=None,
            )

            if done:
                break

    except Exception as e:
        err_msg = str(e)
        print(f"[DEBUG] Task '{task_id}' error: {err_msg}", flush=True)
        log_step(
            step=steps_taken + 1,
            action="ERROR",
            reward=0.0,
            done=True,
            error=err_msg,
        )

    finally:
        # Calculate score: sum of rewards / max possible
        score = sum(rewards) / MAX_TOTAL_REWARD if MAX_TOTAL_REWARD > 0 else 0.0
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_THRESHOLD

        log_end(
            success=success,
            steps=steps_taken,
            score=score,
            rewards=rewards,
        )

    return {
        "task_id": task_id,
        "score": score,
        "rewards": rewards,
        "success": success,
    }


# â”€â”€ Main â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def main() -> None:
    print(f"[DEBUG] Starting inference | model={MODEL_NAME} | env={SPACE_URL}", flush=True)

    # Validate required env vars
    if not HF_TOKEN:
        print("[ERROR] HF_TOKEN environment variable is not set.", flush=True)
        sys.exit(1)

    # Init OpenAI-compatible client
    openai_client = OpenAI(
        base_url=API_BASE_URL,
        api_key=HF_TOKEN,
    )

    # Init environment HTTP client
    env = EnvClient(base_url=SPACE_URL)

    # Verify environment is reachable
    for attempt in range(5):
        try:
            r = requests.get(f"{SPACE_URL}/health", timeout=10)
            r.raise_for_status()
            print(f"[DEBUG] Environment healthy: {r.json()}", flush=True)
            break
        except Exception as e:
            if attempt == 4:
                print(f"[ERROR] Cannot reach environment at {SPACE_URL}: {e}", flush=True)
                sys.exit(1)
            print(f"[DEBUG] Waiting for environment... (attempt {attempt+1}/5)", flush=True)
            time.sleep(3)

    # Run all 3 tasks
    all_results = []
    for task_id in TASKS:
        print(f"\n[DEBUG] â”€â”€ Running task: {task_id} â”€â”€", flush=True)
        result = run_task(env, openai_client, task_id)
        all_results.append(result)

    # Final summary
    overall_score = sum(r["score"] for r in all_results) / len(all_results)

    print("\n[DEBUG] â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•", flush=True)
    print("[DEBUG] FINAL RESULTS", flush=True)
    print("[DEBUG] â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•", flush=True)
    for r in all_results:
        status = "PASS âœ“" if r["success"] else "FAIL âœ—"
        print(f"[DEBUG]   {r['task_id']:8s}  score={r['score']:.3f}  {status}", flush=True)
    print(f"[DEBUG]   OVERALL   score={overall_score:.3f}", flush=True)
    print("[DEBUG] â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•\n", flush=True)


if __name__ == "__main__":
    main()
