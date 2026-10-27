"""LeakeHouse Task Store and Lifecycle State Machine.

Maintains formal task records, execution states, and the 9-point handoff contract.
Supports automated trigger of deployment-agent when task transitions to DONE/DEPLOYED.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class TaskState(StrEnum):
    BACKLOG = "BACKLOG"
    READY = "READY"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    IN_REVIEW = "IN_REVIEW"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    DONE = "DONE"
    DEPLOYED = "DEPLOYED"


# Legal transitions matrix
VALID_TRANSITIONS: dict[TaskState, list[TaskState]] = {
    TaskState.BACKLOG: [TaskState.READY, TaskState.BLOCKED],
    TaskState.READY: [TaskState.IN_PROGRESS, TaskState.BLOCKED],
    TaskState.IN_PROGRESS: [TaskState.IN_REVIEW, TaskState.BLOCKED, TaskState.VERIFICATION_FAILED],
    TaskState.BLOCKED: [TaskState.READY, TaskState.IN_PROGRESS],
    TaskState.IN_REVIEW: [TaskState.DONE, TaskState.VERIFICATION_FAILED, TaskState.BLOCKED],
    TaskState.VERIFICATION_FAILED: [TaskState.IN_PROGRESS, TaskState.BLOCKED],
    TaskState.DONE: [TaskState.DEPLOYED],
    TaskState.DEPLOYED: [],  # Final post-push state
}


class HandoffContract(BaseModel):
    """The mandatory 9-point handoff contract between agents."""

    task_id: str = Field(..., description="Unique task identifier")
    objective: str = Field(..., description="Target objective")
    scope_and_ownership: list[str] = Field(..., description="Allowed file scope")
    context_and_docs: list[str] = Field(default_factory=list, description="Relevant documentation")
    dependencies: list[str] = Field(default_factory=list, description="Upstream dependencies")
    acceptance_criteria: list[str] = Field(..., description="Testable acceptance criteria")
    files_changed: list[str] = Field(default_factory=list, description="Manifest of modified files")
    tests_and_results: dict[str, Any] = Field(
        default_factory=dict, description="Test output and coverage"
    )
    blockers_and_risks: list[str] = Field(
        default_factory=list, description="Identified risks and blockers"
    )
    next_step: str = Field(..., description="Recommended next action or agent handoff")


class TaskRecord(BaseModel):
    """Full task record stored in the task store."""

    id: str
    title: str
    description: str
    assigned_agent: str
    state: TaskState = TaskState.BACKLOG
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    handoffs: list[HandoffContract] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    retry_count: int = 0


class TaskStore:
    """Manages active tasks and enforces state transitions."""

    def __init__(self, storage_path: Path | None = None) -> None:
        self.storage_path = (
            storage_path
            or Path(__file__).resolve().parent.parent / ".state_checkpoints" / "task_store.json"
        )
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.tasks: dict[str, TaskRecord] = {}
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                for task_data in data.values():
                    task = TaskRecord(**task_data)
                    self.tasks[task.id] = task
            except Exception:
                self.tasks = {}

    def _save(self) -> None:
        serialized = {k: v.model_dump() for k, v in self.tasks.items()}
        self.storage_path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")

    def create_task(
        self,
        task_id: str,
        title: str,
        description: str,
        assigned_agent: str,
        metadata: dict[str, Any] | None = None,
    ) -> TaskRecord:
        record = TaskRecord(
            id=task_id,
            title=title,
            description=description,
            assigned_agent=assigned_agent,
            metadata=metadata or {},
        )
        self.tasks[task_id] = record
        self._save()
        return record

    def transition_state(self, task_id: str, new_state: TaskState) -> TaskRecord:
        task = self.tasks.get(task_id)
        if not task:
            raise KeyError(f"Task '{task_id}' not found in TaskStore")

        valid_next_states = VALID_TRANSITIONS.get(task.state, [])
        if new_state not in valid_next_states:
            raise ValueError(
                f"Invalid state transition: cannot transition from {task.state} to {new_state}. "
                f"Valid next states: {valid_next_states}"
            )

        task.state = new_state
        task.updated_at = datetime.now(UTC).isoformat()
        self._save()
        return task

    def add_handoff(self, task_id: str, handoff: HandoffContract) -> TaskRecord:
        task = self.tasks.get(task_id)
        if not task:
            raise KeyError(f"Task '{task_id}' not found in TaskStore")

        task.handoffs.append(handoff)
        task.updated_at = datetime.now(UTC).isoformat()
        self._save()
        return task

    def get_task(self, task_id: str) -> TaskRecord | None:
        return self.tasks.get(task_id)
