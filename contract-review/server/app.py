"""
FastAPI server for the Contract Review RL Environment.
Exposes all required OpenEnv endpoints: /reset, /step, /state, /health.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from .environment import ContractReviewEnvironment

# â”€â”€ App setup â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

app = FastAPI(
    title="Contract Review RL Environment",
    description=(
        "An OpenEnv-compliant RL environment where AI agents review legal contracts "
        "for missing clauses, ambiguous language, and cross-document contradictions."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single shared environment instance
env = ContractReviewEnvironment()


# â”€â”€ Request / Response models â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class ResetRequest(BaseModel):
    task_id: Optional[str] = "easy"


class StepRequest(BaseModel):
    action: Dict[str, Any]


# â”€â”€ Endpoints â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.get("/health")
def health():
    """Health check â€” must return 200 for the pre-submission validator."""
    return {
        "status": "healthy",
        "environment": "contract-review-env",
        "version": "1.0.0",
    }


@app.post("/reset")
def reset(req: Optional[ResetRequest] = None):
    """
    Reset the environment and start a new episode.

    Body (optional):
        { "task_id": "easy" | "medium" | "hard" }

    Returns:
        StepResult: observation, reward=0.0, done=False, info
    """
    task_id = (req.task_id if req and req.task_id else "easy")
    if task_id not in ("easy", "medium", "hard"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid task_id '{task_id}'. Must be 'easy', 'medium', or 'hard'."
        )
    return env.reset(task_id)


@app.post("/step")
def step(req: StepRequest):
    """
    Submit one review action and receive reward + feedback.

    Body:
        {
          "action": {
            "risk_level": "high",
            "missing_clauses": ["indemnification", ...],
            "contradictions": [],
            "flagged_language": ["'as requested' is vague"],
            "review_notes": "This contract lacks..."
          }
        }

    Returns:
        StepResult: observation (with feedback), reward, done, info
    """
    if not req.action:
        raise HTTPException(status_code=400, detail="Action cannot be empty.")
    return env.step(req.action)


@app.get("/state")
def state():
    """
    Return current episode state metadata.

    Returns:
        ContractState: episode_id, step_count, task_id, done, rewards
    """
    return env.get_state()


@app.get("/tasks")
def list_tasks():
    """List all available tasks with descriptions."""
    return {
        "tasks": [
            {
                "id": "easy",
                "name": "Missing Clause Detection",
                "difficulty": "easy",
                "description": "Find missing standard clauses in a vendor service agreement",
            },
            {
                "id": "medium",
                "name": "Ambiguous Language Detection",
                "difficulty": "medium",
                "description": "Identify vague and likely unenforceable clauses in a consulting contract",
            },
            {
                "id": "hard",
                "name": "Cross-Document Contradiction Detection",
                "difficulty": "hard",
                "description": "Detect payment term conflicts between an MSA and SOW",
            },
        ]
    }


@app.get("/")
def root():
    """Root endpoint â€” links to docs."""
    return {
        "name": "Contract Review RL Environment",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "tasks": "/tasks",
    }
    
def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)
    
if __name__ == "__main__":
    main()        
