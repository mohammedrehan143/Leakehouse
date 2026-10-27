"""LeakeHouse Filesystem Tools with Permission Enforcement."""

from __future__ import annotations

from pathlib import Path
from agent_runtime.shared.permissions import verify_write_permission


def safe_write_text(
    agent_id: str,
    file_path: str | Path,
    content: str,
    encoding: str = "utf-8",
) -> Path:
    """Write text to file only if agent possesses authorized write permissions."""
    path = Path(file_path)
    verify_write_permission(agent_id, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=encoding)
    return path


def safe_read_text(file_path: str | Path, encoding: str = "utf-8") -> str:
    """Read file content (all agents hold global read access)."""
    path = Path(file_path)
    return path.read_text(encoding=encoding)
