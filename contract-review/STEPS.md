# Complete Submission Steps — Contract Review Env

## What's in this zip

```
contract-review-env/
├── inference.py         ← Baseline script (runs LLM vs your env)
├── openenv.yaml         ← Metadata file (name, version, tasks)
├── models.py            ← Data types (Action, Observation, State)
├── client.py            ← Python client to talk to your server
├── Dockerfile           ← Container for HF Spaces deployment
├── requirements.txt     ← Python packages
├── pyproject.toml       ← Package config
├── README.md            ← Project description (shown on HF Spaces)
├── test_local.py        ← Quick test script (run before deploying)
├── .env.example         ← Template for your secrets
└── server/
    ├── app.py           ← FastAPI server (endpoints)
    ├── environment.py   ← Core RL logic (reset/step/state)
    └── tasks.py         ← 3 tasks + graders (the creative heart)
```

---

## PART 1 — Local Setup (Day 1)

### Step 1: Install Python packages

```bash
pip install fastapi uvicorn pydantic openai requests openenv-core
```

On some systems you may need:
```bash
pip install fastapi uvicorn pydantic openai requests openenv-core --break-system-packages
```

### Step 2: Start the server

```bash
cd contract-review-env
uvicorn server.app:app --host 0.0.0.0 --port 7860 --reload
```

You should see:
```
INFO: Uvicorn running on http://0.0.0.0:7860
```

Keep this terminal open. Open a NEW terminal for everything else.

### Step 3: Test it works

```bash
# In a new terminal, inside the same folder
python test_local.py
```

All lines should show ✓. If any fail, check the server terminal for errors.

### Step 4: Test manually with curl (optional but helpful)

```bash
# Health check
curl http://localhost:7860/health

# Start an episode (easy task)
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "easy"}'

# Submit a review
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{
    "action": {
      "risk_level": "high",
      "missing_clauses": ["indemnification", "limitation of liability"],
      "contradictions": [],
      "flagged_language": ["services as requested - undefined scope"],
      "review_notes": "This contract is missing critical liability protection clauses."
    }
  }'
```

You'll get a JSON response with reward (0.0–1.0) and feedback.

### Step 5: Open the API docs

Visit http://localhost:7860/docs in your browser.
You'll see all endpoints with interactive test forms. Try them out.

---

## PART 2 — Docker Build (Day 2)

### Step 6: Install Docker

- Mac: https://docs.docker.com/desktop/install/mac-install/
- Windows: https://docs.docker.com/desktop/install/windows-install/
- Ubuntu: `sudo apt-get install docker.io`

### Step 7: Build the Docker image

```bash
# From inside the contract-review-env folder
docker build -t contract-review-env .
```

This takes 1–2 minutes. You should see "Successfully built ..."

### Step 8: Run the Docker container locally

```bash
docker run -p 7860:7860 contract-review-env
```

Test it the same way as before:
```bash
curl http://localhost:7860/health
```

If this works, Docker is ready.

---

## PART 3 — OpenEnv Validation (Day 2)

### Step 9: Run the OpenEnv validator

```bash
# Install the OpenEnv CLI if you haven't
pip install openenv-core

# Run from inside the project folder
openenv validate
```

This checks your openenv.yaml and environment spec.
All 3 checks must pass — this is the pre-submission requirement.

---

## PART 4 — HuggingFace Deployment (Day 3)

### Step 10: Create a HuggingFace account

Go to https://huggingface.co and sign up if you don't have an account.

### Step 11: Get your HF token

Go to https://huggingface.co/settings/tokens
Click "New token" → name it anything → role: "write"
Copy the token (starts with `hf_...`)

### Step 12: Login to HuggingFace CLI

```bash
huggingface-cli login
```

Paste your token when asked.

### Step 13: Deploy to HF Spaces

```bash
openenv push --repo-id YOUR_HF_USERNAME/contract-review-env
```

Replace YOUR_HF_USERNAME with your actual HF username.

This will upload all your files and create a Space at:
`https://huggingface.co/spaces/YOUR_HF_USERNAME/contract-review-env`

The Space URL for API access will be:
`https://YOUR_HF_USERNAME-contract-review-env.hf.space`

### Step 14: Wait for the Space to build

Go to your Space page on HuggingFace.
Wait for the status to change from "Building" to "Running" (2–5 minutes).

### Step 15: Verify the deployed Space works

```bash
curl https://YOUR_HF_USERNAME-contract-review-env.hf.space/health
```

Should return: `{"status": "healthy", ...}`

---

## PART 5 — Run Inference (Day 3)

### Step 16: Set environment variables

**On Mac/Linux:**
```bash
export API_BASE_URL="https://api-inference.huggingface.co/v1"
export MODEL_NAME="meta-llama/Llama-3.3-70B-Instruct"
export HF_TOKEN="hf_YOUR_TOKEN_HERE"
export SPACE_URL="https://YOUR_HF_USERNAME-contract-review-env.hf.space"
```

**On Windows (Command Prompt):**
```cmd
set API_BASE_URL=https://api-inference.huggingface.co/v1
set MODEL_NAME=meta-llama/Llama-3.3-70B-Instruct
set HF_TOKEN=hf_YOUR_TOKEN_HERE
set SPACE_URL=https://YOUR_HF_USERNAME-contract-review-env.hf.space
```

### Step 17: Run the baseline inference

```bash
python inference.py
```

You will see output like:
```
[START] {"task": "easy", "env": "contract-review-env", "model": "..."}
[STEP]  {"step": 1, "action": "...", "reward": 0.72, "done": false, ...}
[STEP]  {"step": 2, "action": "...", "reward": 0.84, "done": true, ...}
[END]   {"success": true, "steps": 2, "score": 0.521, "rewards": [0.72, 0.84]}
...
```

This must complete without errors and produce scores for all 3 tasks.

---

## PART 6 — Submit (Day 3)

### Step 18: Pre-submission validation

Run the pre-submission check script from the hackathon platform:
```bash
# The validator script checks:
# 1. HF Space returns 200 on /reset
# 2. docker build succeeds
# 3. openenv validate passes
```

### Step 19: Submit

Go to the hackathon platform (the OpenEnv dashboard you showed me).
Click "Submit your Assessment".
Paste your HF Space URL:
`https://huggingface.co/spaces/YOUR_HF_USERNAME/contract-review-env`

DEADLINE: April 8, 11:59 PM IST

---

## Troubleshooting

**"Module not found" errors:**
```bash
pip install fastapi uvicorn pydantic openai requests openenv-core --break-system-packages
```

**Server won't start — port in use:**
```bash
uvicorn server.app:app --host 0.0.0.0 --port 8080 --reload
```
(Use 8080 or any free port instead of 7860)

**Docker build fails:**
Make sure Docker Desktop is running (icon in system tray).

**HF Space stays "Building" too long:**
Check the Space logs tab on HuggingFace for errors.
Most common issue: missing package in server/requirements.txt

**inference.py fails with API error:**
- Check HF_TOKEN is set correctly
- Try a different MODEL_NAME: "mistralai/Mistral-7B-Instruct-v0.3"
- Make sure you have HF Pro or the model is free-tier accessible

**reward is always 0.0:**
Your SPACE_URL might be wrong. The URL format for API calls is:
`https://USERNAME-SPACENAME.hf.space` (hyphens, not slashes after username)

---

## Quick Reference: What each file does

| File | Your involvement | Notes |
|------|-----------------|-------|
| server/tasks.py | READ IT — understand the contracts and answers | The grader logic is already written |
| server/environment.py | No changes needed | Handles the episode lifecycle |
| server/app.py | No changes needed | All endpoints are ready |
| models.py | No changes needed | Action/Observation types |
| inference.py | Set env vars only | The LLM agent is already written |
| Dockerfile | No changes needed | Copy-paste ready |
| openenv.yaml | Change author name | Put your name in |
| README.md | Change YOUR_USERNAME | Update the Space URL example |

The only personalisation needed:
1. Change `author` in openenv.yaml to your name
2. Change YOUR_HF_USERNAME to your actual username everywhere
3. Set the 4 environment variables before running inference.py
