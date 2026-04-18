---
title: Contract Review Env
emoji: ⚖️
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
tags:
  - openenv
  - legal
  - contract-review
  - rl-environment
  - real-world
---

# Contract Review RL Environment

An OpenEnv-compliant RL environment where AI agents act as legal contract reviewers. Agents must identify missing clauses, ambiguous language, and cross-document contradictions — skills directly applicable to real-world legal AI.

## Why This Matters

Contract review is a multi-billion dollar problem. Lawyers spend 30–60% of their time on routine contract analysis. An RL environment that trains agents to spot legal risks fills a genuine gap in the agent evaluation ecosystem.

## Environment Description

The agent reads a legal contract (or pair of contracts) and submits a structured review identifying:
- Overall risk level (low / medium / high)
- Missing standard clauses
- Ambiguous or unenforceable language
- Contradictions between related documents

The environment provides graded feedback after each step, enabling multi-step refinement — just like a real review cycle.

## Action Space

```python
ContractAction(
    risk_level: str,           # "low" | "medium" | "high"
    missing_clauses: List[str], # e.g. ["indemnification", "limitation of liability"]
    contradictions: List[str],  # cross-document conflicts
    flagged_language: List[str],# specific problematic phrases
    review_notes: str           # detailed explanation
)
```

## Observation Space

```python
ContractObservation(
    contract_text: str,      # full contract text to review
    task_description: str,   # what to look for
    feedback: str,           # grader feedback from previous step
    step_number: int,        # current step in episode
    hints: List[str]         # optional hints if agent is struggling
)
```

## Tasks

| Task | Name | Difficulty | What to Find |
|------|------|------------|--------------|
| `easy` | Missing Clause Detection | Easy | Standard clauses absent from a vendor agreement |
| `medium` | Ambiguous Language Detection | Medium | Vague compensation + unenforceable non-compete |
| `hard` | Cross-Document Contradiction | Hard | Payment term conflict between MSA and SOW |

## Reward Function

Each step returns a reward `0.0–1.0`:
- **Risk level**: 0.25 weight
- **Missing clauses** (partial credit per clause): 0.40 weight  
- **Domain-specific issues** (contradictions, ambiguity, enforceability): 0.35 weight

Partial credit rewards incremental progress. Feedback after each step guides improvement. Episode terminates after 3 steps or when score ≥ 0.95.

## Baseline Scores

| Task | GPT-4o-mini | Random |
|------|-------------|--------|
| easy | ~0.72 | ~0.08 |
| medium | ~0.61 | ~0.06 |
| hard | ~0.55 | ~0.04 |

## Setup & Usage

### Prerequisites
```bash
pip install openenv-core fastapi uvicorn openai requests
```

### Run locally
```bash
# Start the server
uvicorn server.app:app --host 0.0.0.0 --port 7860 --reload

# In another terminal, test it
curl -X POST http://localhost:7860/reset -H "Content-Type: application/json" -d '{"task_id": "easy"}'
```

### Run with Docker
```bash
docker build -t contract-review-env .
docker run -p 7860:7860 contract-review-env
```

### Run inference
```bash
export API_BASE_URL="https://api-inference.huggingface.co/v1"
export MODEL_NAME="meta-llama/Llama-3.3-70B-Instruct"
export HF_TOKEN="your_hf_token_here"
export SPACE_URL="https://YOUR_USERNAME-contract-review-env.hf.space"

python inference.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/reset` | POST | Start new episode `{"task_id": "easy"}` |
| `/step` | POST | Submit review `{"action": {...}}` |
| `/state` | GET | Current episode state |
| `/tasks` | GET | List available tasks |

## Project Structure

```
contract-review-env/
├── inference.py        ← Baseline inference script (required)
├── openenv.yaml        ← OpenEnv spec manifest
├── models.py           ← Typed Action/Observation/State
├── client.py           ← HTTP client for the environment
├── Dockerfile          ← Container definition
├── pyproject.toml      ← Python package config
├── README.md           ← This file
└── server/
    ├── app.py          ← FastAPI server
    ├── environment.py  ← Core environment logic
    └── tasks.py        ← Task definitions + graders
```
