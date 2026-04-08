#!/usr/bin/env python3
"""
Quick local test â€” run this BEFORE deploying to verify your environment works.

Usage:
    # Terminal 1: start the server
    uvicorn server.app:app --host 0.0.0.0 --port 7860 --reload

    # Terminal 2: run this test
    python test_local.py
"""

import json
import sys
import requests

BASE_URL = "http://localhost:7860"


def test(name: str, passed: bool, detail: str = ""):
    icon = "âœ“" if passed else "âœ—"
    print(f"  {icon}  {name}" + (f"  |  {detail}" if detail else ""))
    return passed


def main():
    print("\nâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
    print("  Contract Review Env â€” Local Tests")
    print("â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•\n")

    all_passed = True

    # â”€â”€ Health check â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("1. Health check")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        ok = test("/health returns 200", r.status_code == 200, str(r.json()))
        all_passed = all_passed and ok
    except Exception as e:
        test("/health reachable", False, str(e))
        print("\n  â†’ Is the server running? Start it with:")
        print("    uvicorn server.app:app --host 0.0.0.0 --port 7860\n")
        sys.exit(1)

    # â”€â”€ Task listing â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\n2. Task listing")
    r = requests.get(f"{BASE_URL}/tasks")
    tasks = r.json().get("tasks", [])
    ok = test("/tasks returns 3 tasks", len(tasks) == 3, str([t["id"] for t in tasks]))
    all_passed = all_passed and ok

    # â”€â”€ Run each task â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    for task_id in ["easy", "medium", "hard"]:
        print(f"\n3. Task: {task_id}")

        # Reset
        r = requests.post(f"{BASE_URL}/reset", json={"task_id": task_id})
        ok = test("reset() returns 200", r.status_code == 200)
        all_passed = all_passed and ok

        data = r.json()
        has_contract = bool(data.get("observation", {}).get("contract_text"))
        ok = test("observation has contract_text", has_contract,
                  f"{len(data.get('observation',{}).get('contract_text',''))} chars")
        all_passed = all_passed and ok

        # Step with a sample review
        sample_action = {
            "risk_level": "high",
            "missing_clauses": ["indemnification", "limitation of liability"],
            "contradictions": [],
            "flagged_language": ["as requested (vague scope)"],
            "review_notes": "This contract is missing critical liability protection clauses.",
        }
        r = requests.post(f"{BASE_URL}/step", json={"action": sample_action})
        ok = test("step() returns 200", r.status_code == 200)
        all_passed = all_passed and ok

        step_data = r.json()
        reward = step_data.get("reward", -1)
        ok = test("reward is 0.0â€“1.0", 0.0 <= reward <= 1.0, f"reward={reward}")
        all_passed = all_passed and ok

        has_feedback = bool(step_data.get("observation", {}).get("feedback"))
        ok = test("observation has feedback", has_feedback,
                  step_data.get("observation", {}).get("feedback", "")[:60])
        all_passed = all_passed and ok

        # State
        r = requests.get(f"{BASE_URL}/state")
        ok = test("state() returns 200", r.status_code == 200)
        all_passed = all_passed and ok

    # â”€â”€ Summary â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
    if all_passed:
        print("  ALL TESTS PASSED  âœ“  Ready to deploy!")
        print("\n  Next steps:")
        print("    1. openenv validate")
        print("    2. docker build -t contract-review-env .")
        print("    3. openenv push --repo-id YOUR_USER/contract-review-env")
    else:
        print("  SOME TESTS FAILED  âœ—  Fix errors before deploying.")
    print("â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•\n")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
