"""LeakeHouse Git Execution Tools.

Provides high-level programmatic interfaces to git operations for the deployment agent.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def run_git(args: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Execute a git command and return (exit_code, stdout, stderr)."""
    work_dir = cwd or Path.cwd()
    cmd = ["git"] + args
    result = subprocess.run(
        cmd,
        cwd=str(work_dir),
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def get_git_status(cwd: Path | None = None) -> list[dict[str, str]]:
    """Return parsed porcelain git status entries."""
    code, out, err = run_git(["status", "--porcelain"], cwd=cwd)
    if code != 0:
        raise RuntimeError(f"Git status failed: {err}")

    entries = []
    for line in out.splitlines():
        if len(line) >= 4:
            status = line[:2].strip()
            filepath = line[3:].strip()
            entries.append({"status": status, "path": filepath})
    return entries


def get_current_branch(cwd: Path | None = None) -> str:
    """Return the name of the current git branch."""
    code, out, err = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
    if code != 0:
        raise RuntimeError(f"Failed to get current branch: {err}")
    return out


def get_remote_url(remote: str = "origin", cwd: Path | None = None) -> str:
    """Return the remote URL for a given remote name."""
    code, out, err = run_git(["remote", "get-url", remote], cwd=cwd)
    if code != 0:
        raise RuntimeError(f"Failed to get remote URL for '{remote}': {err}")
    return out


def stage_all(cwd: Path | None = None) -> None:
    """Stage all tracked and untracked changes."""
    code, _, err = run_git(["add", "-A"], cwd=cwd)
    if code != 0:
        raise RuntimeError(f"Git add failed: {err}")


def stage_files(files: list[str], cwd: Path | None = None) -> None:
    """Stage specific files."""
    code, _, err = run_git(["add"] + files, cwd=cwd)
    if code != 0:
        raise RuntimeError(f"Git add failed for {files}: {err}")


def commit_changes(message: str, cwd: Path | None = None) -> str:
    """Commit staged changes and return commit hash."""
    code, out, err = run_git(["commit", "-m", message], cwd=cwd)
    if code != 0:
        raise RuntimeError(f"Git commit failed: {err}")

    # Retrieve HEAD commit hash
    code_hash, out_hash, err_hash = run_git(["rev-parse", "--short", "HEAD"], cwd=cwd)
    if code_hash == 0:
        return out_hash
    return "UNKNOWN"


def push_to_remote(remote: str = "origin", branch: str = "main", cwd: Path | None = None) -> str:
    """Push commits to specified remote and branch."""
    code, out, err = run_git(["push", remote, branch], cwd=cwd)
    if code != 0:
        raise RuntimeError(f"Git push to {remote}/{branch} failed: {err}")
    return out or err or "Everything up-to-date"


def has_uncommitted_changes(cwd: Path | None = None) -> bool:
    """Check if there are modified, added, or deleted files in the working directory."""
    entries = get_git_status(cwd=cwd)
    return len(entries) > 0
