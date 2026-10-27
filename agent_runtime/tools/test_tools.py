"""LeakeHouse Test and Verification Tools."""

from __future__ import annotations

import subprocess
from pathlib import Path


def run_pytest(test_path: str = "agent_runtime/tests", cwd: Path | None = None) -> tuple[int, str]:
    """Execute pytest and return (exit_code, output)."""
    work_dir = cwd or Path.cwd()
    cmd = ["python", "-m", "pytest", test_path]
    result = subprocess.run(
        cmd,
        cwd=str(work_dir),
        capture_output=True,
        text=True,
        check=False,
    )
    combined = result.stdout + "\n" + result.stderr
    return result.returncode, combined.strip()
