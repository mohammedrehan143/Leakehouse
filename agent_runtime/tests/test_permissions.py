"""Unit tests for permission and file ownership enforcement."""

import pytest
from agent_runtime.shared.permissions import (
    PermissionDeniedError,
    can_write,
    verify_write_permission,
)


def test_master_orchestrator_permissions():
    assert can_write("master-orchestrator", "AGENTS.md")
    assert can_write("master-orchestrator", "backend/src/routes.py")


def test_domain_agent_permissions():
    assert can_write("api-engineer", "backend/src/leakehouse/api/routes.py")
    assert not can_write("api-engineer", "frontend/src/App.tsx")

    assert can_write("frontend-engineer", "frontend/src/App.tsx")
    assert not can_write("frontend-engineer", "backend/src/leakehouse/storage/models.py")


def test_permission_denial_exception():
    with pytest.raises(PermissionDeniedError):
        verify_write_permission("ui-ux-engineer", "backend/src/leakehouse/api/routes.py")
