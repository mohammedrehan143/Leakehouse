"""Unit tests for DeploymentAgent verification."""

from unittest.mock import MagicMock, patch
from pathlib import Path
from agent_runtime.deployment.deployment_agent import DeploymentAgent
from agent_runtime.shared.task_store import TaskStore, TaskState


def test_deployment_agent_init(tmp_path: Path):
    store = TaskStore(storage_path=tmp_path / "tasks.json")
    agent = DeploymentAgent(repo_dir=tmp_path, task_store=store)

    assert agent.repo_dir == tmp_path
    assert agent.DEFAULT_REPO == "https://github.com/mohammedrehan143/Leakehouse.git"
    assert agent.DEFAULT_BRANCH == "main"


@patch("agent_runtime.deployment.deployment_agent.has_uncommitted_changes")
@patch("agent_runtime.deployment.deployment_agent.push_to_remote")
def test_deploy_task_up_to_date(mock_push, mock_has_changes, tmp_path: Path):
    mock_has_changes.return_value = False
    mock_push.return_value = "Everything up-to-date"

    store = TaskStore(storage_path=tmp_path / "tasks.json")
    agent = DeploymentAgent(repo_dir=tmp_path, task_store=store)

    receipt = agent.deploy_task()
    assert receipt.status == "UP_TO_DATE"
    assert receipt.target_repo == "https://github.com/mohammedrehan143/Leakehouse.git"


@patch("agent_runtime.deployment.deployment_agent.has_uncommitted_changes")
@patch("agent_runtime.deployment.deployment_agent.get_git_status")
@patch("agent_runtime.deployment.deployment_agent.stage_all")
@patch("agent_runtime.deployment.deployment_agent.commit_changes")
@patch("agent_runtime.deployment.deployment_agent.push_to_remote")
def test_deploy_task_commit_and_push(
    mock_push,
    mock_commit,
    mock_stage,
    mock_status,
    mock_has_changes,
    tmp_path: Path,
):
    mock_has_changes.return_value = True
    mock_status.return_value = [{"status": "M", "path": "test.txt"}]
    mock_commit.return_value = "abc1234"
    mock_push.return_value = "To https://github.com/mohammedrehan143/Leakehouse.git main -> main"

    store = TaskStore(storage_path=tmp_path / "tasks.json")
    task = store.create_task("TASK-999", "Deploy Test", "Test", "deployment-agent")
    store.transition_state("TASK-999", TaskState.READY)
    store.transition_state("TASK-999", TaskState.IN_PROGRESS)
    store.transition_state("TASK-999", TaskState.IN_REVIEW)
    store.transition_state("TASK-999", TaskState.DONE)

    agent = DeploymentAgent(repo_dir=tmp_path, task_store=store)
    receipt = agent.deploy_task(task_id="TASK-999", commit_message="feat: test commit")

    assert receipt.status == "SUCCESS"
    assert receipt.commit_hash == "abc1234"
    assert "test.txt" in receipt.files_pushed
    assert store.get_task("TASK-999").state == TaskState.DEPLOYED
