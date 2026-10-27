"""Typed state and task contracts for the Multi-Agent System."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class TaskExecutionStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ToolCallRecord(BaseModel):
    """Log of a controlled tool invocation."""

    tool_name: str
    arguments: dict[str, Any]
    output: Any
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    duration_ms: float = 0.0


class AgentTaskState(BaseModel):
    """Unified state container passed through the agent orchestration graph."""

    task_id: str
    user_query: str
    status: TaskExecutionStatus = TaskExecutionStatus.PENDING
    assigned_specialist: str | None = None
    plan: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)
    tool_history: list[ToolCallRecord] = Field(default_factory=list)
    requires_approval: bool = False
    approved: bool = False
    error: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
