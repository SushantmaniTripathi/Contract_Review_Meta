"""
HTTP client for the Contract Review RL Environment.
Use this to interact with the environment from your training code.
"""

import requests
import subprocess
import time
import atexit
from typing import Optional
from models import ContractAction, ContractObservation, ContractState, StepResult


class ContractReviewClient:
    """
    HTTP client for the Contract Review environment.

    Usage (against running server or HF Space):
        client = ContractReviewClient("http://localhost:7860")
        result = client.reset("easy")
        result = client.step(ContractAction(
            risk_level="high",
            missing_clauses=["indemnification"],
            review_notes="This contract lacks..."
        ))

    Usage (auto-start from Docker image):
        client = ContractReviewClient.from_docker_image("contract-review-env:latest")
        result = client.reset("easy")
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._container_id: Optional[str] = None

    @classmethod
    def from_docker_image(cls, image_name: str, port: int = 7860) -> "ContractReviewClient":
        """Start a Docker container and return a connected client."""
        print(f"[ContractReviewClient] Starting Docker container from {image_name}...")
        result = subprocess.run(
            ["docker", "run", "-d", "-p", f"{port}:7860", image_name],
            capture_output=True, text=True, check=True
        )
        container_id = result.stdout.strip()
        client = cls(f"http://localhost:{port}")
        client._container_id = container_id

        # Wait for the container to be ready
        for attempt in range(30):
            try:
                r = requests.get(f"http://localhost:{port}/health", timeout=2)
                if r.status_code == 200:
                    print(f"[ContractReviewClient] Container ready at port {port}")
                    break
            except Exception:
                pass
            time.sleep(1)
        else:
            raise RuntimeError("Container did not become healthy in 30 seconds")

        # Register cleanup
        atexit.register(client.close)
        return client

    def reset(self, task_id: str = "easy") -> StepResult:
        """Start a new episode for the given task."""
        r = requests.post(
            f"{self.base_url}/reset",
            json={"task_id": task_id},
            timeout=30
        )
        r.raise_for_status()
        data = r.json()
        return StepResult(
            observation=ContractObservation(**data["observation"]),
            reward=data.get("reward", 0.0),
            done=data.get("done", False),
            info=data.get("info", {})
        )

    def step(self, action: ContractAction) -> StepResult:
        """Submit a review action and get feedback + reward."""
        r = requests.post(
            f"{self.base_url}/step",
            json={"action": action.model_dump()},
            timeout=30
        )
        r.raise_for_status()
        data = r.json()
        return StepResult(
            observation=ContractObservation(**data["observation"]),
            reward=data.get("reward", 0.0),
            done=data.get("done", False),
            info=data.get("info", {})
        )

    def state(self) -> ContractState:
        """Get current episode state."""
        r = requests.get(f"{self.base_url}/state", timeout=10)
        r.raise_for_status()
        return ContractState(**r.json())

    def health(self) -> bool:
        """Check if the server is running."""
        try:
            r = requests.get(f"{self.base_url}/health", timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def close(self):
        """Stop the Docker container if we started one."""
        if self._container_id:
            try:
                subprocess.run(
                    ["docker", "stop", self._container_id],
                    capture_output=True, check=True
                )
                print(f"[ContractReviewClient] Container {self._container_id[:12]} stopped.")
            except Exception as e:
                print(f"[ContractReviewClient] Could not stop container: {e}")
            self._container_id = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
