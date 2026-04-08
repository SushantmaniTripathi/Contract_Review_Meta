"""
Typed Pydantic models for the Contract Review RL Environment.
Defines the Action, Observation, and State interfaces.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ContractAction(BaseModel):
    """
    Action submitted by the agent: a structured legal contract review.
    """
    risk_level: str = Field(
        description="Overall risk assessment: 'low', 'medium', or 'high'",
        examples=["high"]
    )
    missing_clauses: List[str] = Field(
        default=[],
        description="Names of standard clauses that are absent from the contract",
        examples=[["indemnification", "limitation of liability"]]
    )
    contradictions: List[str] = Field(
        default=[],
        description="Conflicts found between different parts or documents",
        examples=[["MSA requires Net-60 but SOW specifies Net-30"]]
    )
    flagged_language: List[str] = Field(
        default=[],
        description="Specific problematic phrases or clauses quoted from the contract",
        examples=[["'fair and reasonable compensation' - no specific amount defined"]]
    )
    review_notes: str = Field(
        description="Detailed explanation of all identified issues and risks",
        examples=["This agreement is missing critical liability protections..."]
    )


class ContractObservation(BaseModel):
    """
    Observation returned to the agent after reset() or step().
    """
    contract_text: str = Field(
        description="The full contract text the agent must review"
    )
    task_description: str = Field(
        description="Instructions explaining what to look for in this task"
    )
    feedback: str = Field(
        default="",
        description="Grader feedback from the previous step (empty on first step)"
    )
    step_number: int = Field(
        default=0,
        description="Current step number in this episode (0 = just reset)"
    )
    hints: List[str] = Field(
        default=[],
        description="Optional hints provided when the agent is struggling"
    )


class ContractState(BaseModel):
    """
    Episode metadata returned by state().
    """
    episode_id: str = Field(description="Unique ID for the current episode")
    step_count: int = Field(description="Number of steps taken so far")
    task_id: str = Field(description="Current task: 'easy', 'medium', or 'hard'")
    max_steps: int = Field(default=3, description="Maximum steps per episode")
    done: bool = Field(default=False, description="Whether the episode has ended")
    cumulative_reward: float = Field(default=0.0, description="Sum of all rewards so far")
    best_reward: float = Field(default=0.0, description="Highest reward achieved in this episode")


class StepResult(BaseModel):
    """
    Result returned by both reset() and step().
    """
    observation: ContractObservation
    reward: float = Field(default=0.0, description="Reward for this step (0.0â€“1.0)")
    done: bool = Field(default=False, description="True if episode is complete")
    info: Dict[str, Any] = Field(default_factory=dict, description="Extra metadata")
