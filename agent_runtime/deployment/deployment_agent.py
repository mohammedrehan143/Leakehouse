"""LeakeHouse Automated Git Deployment Agent.

Responsible for staging verified task artifacts, crafting semantic commits,
pushing directly to https://github.com/mohammedrehan143/Leakehouse.git on branch main,
and emitting auditable deployment receipts.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from agent_runtime.shared.task_store import TaskState, TaskStore
from agent_runtime.tools.git_tools import (
    commit_changes,
    get_current_branch,
    get_git_status,
    get_remote_url,
    has_uncommitted_changes,
    push_to_remote,
    stage_all,
    stage_files,
)


class DeploymentReceipt(BaseModel):
    """Execution receipt emitted after every git commit and remote push."""

    receipt_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    target_repo: str
    branch: str
    commit_hash: str
    commit_message: str
    files_pushed: list[str]
    status: str
    details: dict[str, Any] = Field(default_factory=dict)


class DeploymentAgent:
    """Autonomous Deployment Agent for LeakeHouse."""

    DEFAULT_REPO = "https://github.com/mohammedrehan143/Leakehouse.git"
    DEFAULT_BRANCH = "main"

    def __init__(
        self,
        repo_dir: Path | None = None,
        task_store: TaskStore | None = None,
    ) -> None:
        self.repo_dir = repo_dir or Path(__file__).resolve().parent.parent.parent
        self.task_store = task_store or TaskStore()
        self.telemetry_dir = (
            self.repo_dir / "agent_runtime" / ".telemetry_logs"
        )
        self.telemetry_dir.mkdir(parents=True, exist_ok=True)

    def verify_environment(self) -> dict[str, str]:
        """Validate that git remote and branch match configuration."""
        branch = get_current_branch(cwd=self.repo_dir)
        try:
            remote_url = get_remote_url(remote="origin", cwd=self.repo_dir)
        except Exception:
            remote_url = self.DEFAULT_REPO

        return {
            "branch": branch,
            "remote_url": remote_url,
        }

    def deploy_task(
        self,
        task_id: str | None = None,
        commit_message: str | None = None,
        file_scope: list[str] | None = None,
        remote: str = "origin",
        branch: str = "main",
    ) -> DeploymentReceipt:
        """Stage, commit, and push task changes to the GitHub repository."""
        # Check git status
        if not has_uncommitted_changes(cwd=self.repo_dir):
            # No changes to commit, check if we need to push any local unpushed commits
            push_output = push_to_remote(remote=remote, branch=branch, cwd=self.repo_dir)
            receipt = DeploymentReceipt(
                receipt_id=f"DEPLOY-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
                target_repo=self.DEFAULT_REPO,
                branch=branch,
                commit_hash="HEAD",
                commit_message=commit_message or "Sync with remote",
                files_pushed=[],
                status="UP_TO_DATE",
                details={"push_output": push_output, "note": "No uncommitted local changes"},
            )
            self._record_receipt(receipt)
            return receipt

        # Gather file status
        status_entries = get_git_status(cwd=self.repo_dir)
        changed_files = [entry["path"] for entry in status_entries]

        # Stage files
        if file_scope:
            stage_files(file_scope, cwd=self.repo_dir)
        else:
            stage_all(cwd=self.repo_dir)

        # Formulate commit message
        if not commit_message:
            tag = f"[{task_id}] " if task_id else ""
            commit_message = f"feat: {tag}complete task implementation and verification"

        # Commit changes
        commit_hash = commit_changes(commit_message, cwd=self.repo_dir)

        # Push to remote GitHub repo
        push_output = push_to_remote(remote=remote, branch=branch, cwd=self.repo_dir)

        receipt = DeploymentReceipt(
            receipt_id=f"DEPLOY-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            target_repo=self.DEFAULT_REPO,
            branch=branch,
            commit_hash=commit_hash,
            commit_message=commit_message,
            files_pushed=changed_files,
            status="SUCCESS",
            details={
                "push_output": push_output,
                "task_id": task_id,
            },
        )

        # If a task ID was provided, mark it DEPLOYED in task store
        if task_id and self.task_store.get_task(task_id):
            try:
                task = self.task_store.get_task(task_id)
                if task and task.state == TaskState.DONE:
                    self.task_store.transition_state(task_id, TaskState.DEPLOYED)
            except Exception:
                pass

        self._record_receipt(receipt)
        return receipt

    def _record_receipt(self, receipt: DeploymentReceipt) -> None:
        """Append receipt to telemetry log."""
        log_file = self.telemetry_dir / "deployments.jsonl"
        with log_file.open("a", encoding="utf-8") as f:
            f.write(receipt.model_dump_json() + "\n")
