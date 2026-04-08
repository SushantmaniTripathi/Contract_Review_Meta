"""
Core environment logic for the Contract Review RL Environment.
Implements reset(), step(), and state() per the OpenEnv spec.
"""

import uuid
from typing import Any, Dict
from .tasks import TASKS, grade_action


class ContractReviewEnvironment:
    """
    A multi-step RL environment for legal contract review.

    Episode flow:
      1. reset(task_id)  â†’ agent receives contract + task description
      2. step(action)    â†’ agent submits review â†’ reward + feedback returned
      3. Repeat step up to max_steps times (agent improves based on feedback)
      4. done=True when max_steps reached or reward >= 0.95 (solved)
    """

    def __init__(self):
        self._episode_id = ""
        self._step_count = 0
        self._task_id = "easy"
        self._max_steps = 3
        self._done = False
        self._cumulative_reward = 0.0
        self._best_reward = 0.0
        self._last_feedback = ""
        self._last_hints = []
        self._current_task = None

    # â”€â”€ Public API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def reset(self, task_id: str = "easy") -> Dict[str, Any]:
        """
        Start a new episode for the given task.
        Returns a StepResult-shaped dict (observation, reward, done, info).
        """
        if task_id not in TASKS:
            task_id = "easy"

        self._episode_id = str(uuid.uuid4())
        self._task_id = task_id
        self._step_count = 0
        self._done = False
        self._cumulative_reward = 0.0
        self._best_reward = 0.0
        self._last_feedback = ""
        self._last_hints = []
        self._current_task = TASKS[task_id]
        self._max_steps = self._current_task["max_steps"]

        return {
            "observation": {
                "contract_text": self._current_task["contract"].strip(),
                "task_description": self._current_task["description"].strip(),
                "feedback": "",
                "step_number": 0,
                "hints": [],
            },
            "reward": 0.0,
            "done": False,
            "info": {
                "episode_id": self._episode_id,
                "task_id": task_id,
                "task_name": self._current_task["name"],
                "max_steps": self._max_steps,
            },
        }

    def step(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute one review step.
        action must contain keys: risk_level, missing_clauses, contradictions,
                                   flagged_language, review_notes
        Returns observation with feedback, reward (0-1), done flag, and info.
        """
        if self._done or self._current_task is None:
            return {
                "observation": {
                    "contract_text": "",
                    "task_description": "",
                    "feedback": "Episode is over. Call reset() to start a new episode.",
                    "step_number": self._step_count,
                    "hints": [],
                },
                "reward": 0.0,
                "done": True,
                "info": {"error": "Episode already complete"},
            }

        self._step_count += 1

        # Grade the action
        reward, feedback, hints = grade_action(
            task_id=self._task_id,
            action=action,
            step=self._step_count,
        )

        self._cumulative_reward += reward
        self._best_reward = max(self._best_reward, reward)
        self._last_feedback = feedback
        self._last_hints = hints

        # Terminal conditions
        done = (self._step_count >= self._max_steps) or (reward >= 0.95)
        self._done = done

        return {
            "observation": {
                "contract_text": self._current_task["contract"].strip(),
                "task_description": self._current_task["description"].strip(),
                "feedback": feedback,
                "step_number": self._step_count,
                "hints": hints if not done else [],
            },
            "reward": reward,
            "done": done,
            "info": {
                "episode_id": self._episode_id,
                "step": self._step_count,
                "max_steps": self._max_steps,
                "cumulative_reward": round(self._cumulative_reward, 4),
                "best_reward": round(self._best_reward, 4),
            },
        }

    def get_state(self) -> Dict[str, Any]:
        """Return current episode metadata."""
        return {
            "episode_id": self._episode_id,
            "step_count": self._step_count,
            "task_id": self._task_id,
            "max_steps": self._max_steps,
            "done": self._done,
            "cumulative_reward": round(self._cumulative_reward, 4),
            "best_reward": round(self._best_reward, 4),
        }
