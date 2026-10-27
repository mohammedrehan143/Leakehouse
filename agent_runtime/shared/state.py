"""LeakeHouse Shared Execution State."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    """Contextual metadata passed during agent delegation."""

    agent_id: str
    active_task_id: str | None = None
    permissions: list[str] = Field(default_factory=list)
    environment: dict[str, Any] = Field(default_factory=dict)
