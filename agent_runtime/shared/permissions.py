"""LeakeHouse File Ownership and Permission Enforcement Engine."""

from __future__ import annotations

import fnmatch
from pathlib import Path


class PermissionDeniedError(PermissionError):
    """Raised when an agent attempts to access or modify a file outside its scope."""


# Normalized mapping of agent identifier to glob patterns of permitted write files
FILE_OWNERSHIP_MATRIX: dict[str, list[str]] = {
    "master-orchestrator": [
        ".agents/tasks/*",
        ".agents/policies/*",
        "agent_runtime/master/*",
        "AGENTS.md",
        "README.md",
    ],
    "deployment-agent": [
        ".agents/tasks/*",
        ".agents/policies/deployment-policy.md",
        "agent_runtime/deployment/*",
        ".git/*",
    ],
    "backend-orchestrator": [
        "backend/*",
        "agent_runtime/backend/*",
    ],
    "frontend-orchestrator": [
        "frontend/*",
        "agent_runtime/frontend/*",
    ],
    "api-engineer": [
        "backend/src/leakehouse/api/*",
        "docs/api-contracts.md",
    ],
    "database-engineer": [
        "backend/src/leakehouse/storage/*",
        "backend/migrations/*",
    ],
    "ingestion-engineer": [
        "backend/src/leakehouse/ingestion/*",
    ],
    "pipeline-engineer": [
        "backend/src/leakehouse/pipeline/*",
    ],
    "backend-security-engineer": [
        "backend/src/leakehouse/common/security.py",
        ".agents/policies/security-rules.md",
    ],
    "backend-test-engineer": [
        "backend/tests/*",
    ],
    "ui-ux-engineer": [
        "frontend/src/components/design-system/*",
        "frontend/src/styles/*",
    ],
    "frontend-engineer": [
        "frontend/src/App.tsx",
        "frontend/src/main.tsx",
        "frontend/src/components/*",
        "frontend/src/layouts/*",
    ],
    "dashboard-engineer": [
        "frontend/src/charts/*",
        "frontend/src/pages/*",
        "frontend/src/components/widgets/*",
    ],
    "api-integration-engineer": [
        "frontend/src/services/*",
        "frontend/src/types/*",
    ],
    "accessibility-engineer": [
        "frontend/src/**/*",
    ],
    "frontend-test-engineer": [
        "frontend/tests/*",
        "frontend/src/**/*.test.tsx",
    ],
    "software-architect": [
        "docs/*",
        ".agents/tasks/contracts.md",
    ],
    "integration-engineer": [
        "agent_runtime/tests/integration/*",
        "tests/e2e/*",
    ],
    "devops-engineer": [
        "docker-compose.yml",
        "Makefile",
        "infra/*",
        ".github/workflows/*",
        ".env.example",
    ],
    "independent-code-reviewer": [
        ".agents/tasks/current-task.md",
    ],
}


def can_write(agent_id: str, file_path: str | Path) -> bool:
    """Evaluate whether the specified agent holds write authorization for file_path."""
    # Master orchestrator and deployment agent have broad coordination scopes
    if agent_id == "master-orchestrator":
        return True

    allowed_patterns = FILE_OWNERSHIP_MATRIX.get(agent_id, [])
    norm_path = str(file_path).replace("\\", "/").lstrip("./")

    for pattern in allowed_patterns:
        norm_pattern = pattern.replace("\\", "/").lstrip("./")
        if fnmatch.fnmatch(norm_path, norm_pattern):
            return True
        if norm_pattern.endswith("/*"):
            prefix = norm_pattern[:-2]
            if norm_path.startswith(prefix):
                return True
    return False


def verify_write_permission(agent_id: str, file_path: str | Path) -> None:
    """Raises PermissionDeniedError if agent is unauthorized to write to file_path."""
    if not can_write(agent_id, file_path):
        raise PermissionDeniedError(
            f"Agent '{agent_id}' is not authorized to modify '{file_path}'. "
            f"Allowed file patterns: {FILE_OWNERSHIP_MATRIX.get(agent_id, [])}"
        )
