"""Unit tests for LeakeHouse TaskStore and state machine."""

import pytest
from pathlib import Path
from agent_runtime.shared.task_store import TaskStore, TaskState, HandoffContract


def test_task_creation_and_transition(tmp_path: Path):
    store_file = tmp_path / "tasks.json"
    store = TaskStore(storage_path=store_file)

    task = store.create_task(
        task_id="TASK-001",
        title="Test Task",
        description="A test task",
        assigned_agent="backend-orchestrator",
    )

    assert task.state == TaskState.BACKLOG

    # Valid transitions: BACKLOG -> READY -> IN_PROGRESS -> IN_REVIEW -> DONE -> DEPLOYED
    store.transition_state("TASK-001", TaskState.READY)
    assert store.get_task("TASK-001").state == TaskState.READY

    store.transition_state("TASK-001", TaskState.IN_PROGRESS)
    assert store.get_task("TASK-001").state == TaskState.IN_PROGRESS

    store.transition_state("TASK-001", TaskState.IN_REVIEW)
    assert store.get_task("TASK-001").state == TaskState.IN_REVIEW

    store.transition_state("TASK-001", TaskState.DONE)
    assert store.get_task("TASK-001").state == TaskState.DONE

    store.transition_state("TASK-001", TaskState.DEPLOYED)
    assert store.get_task("TASK-001").state == TaskState.DEPLOYED


def test_invalid_transition(tmp_path: Path):
    store_file = tmp_path / "tasks.json"
    store = TaskStore(storage_path=store_file)

    store.create_task(
        task_id="TASK-002",
        title="Invalid Transition Test",
        description="Testing illegal transition",
        assigned_agent="frontend-orchestrator",
    )

    # Illegal transition: BACKLOG directly to DONE
    with pytest.raises(ValueError):
        store.transition_state("TASK-002", TaskState.DONE)


def test_handoff_contract(tmp_path: Path):
    store_file = tmp_path / "tasks.json"
    store = TaskStore(storage_path=store_file)

    store.create_task(
        task_id="TASK-003",
        title="Handoff Test",
        description="Testing 9-point contract",
        assigned_agent="api-engineer",
    )

    handoff = HandoffContract(
        task_id="TASK-003",
        objective="Create health check endpoint",
        scope_and_ownership=["backend/src/leakehouse/api/routes.py"],
        context_and_docs=["docs/api-contracts.md"],
        dependencies=[],
        acceptance_criteria=["GET /api/v1/health returns 200 OK"],
        files_changed=["backend/src/leakehouse/api/routes.py"],
        tests_and_results={"passed": 2, "failed": 0},
        blockers_and_risks=[],
        next_step="Trigger deployment-agent",
    )

    updated_task = store.add_handoff("TASK-003", handoff)
    assert len(updated_task.handoffs) == 1
    assert updated_task.handoffs[0].task_id == "TASK-003"
