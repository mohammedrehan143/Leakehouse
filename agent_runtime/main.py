"""LeakeHouse Agent Runtime Main Entrypoint."""

from __future__ import annotations

import argparse
import sys
from agent_runtime.deployment.deployment_agent import DeploymentAgent
from agent_runtime.shared.task_store import TaskStore


def main() -> None:
    parser = argparse.ArgumentParser(description="LeakeHouse Multi-Agent Runtime Engine")
    parser.add_argument("--status", action="store_true", help="Display current task and agent status")
    parser.add_argument("--deploy", action="store_true", help="Trigger deployment agent push")
    parser.add_argument("--message", type=str, default="chore: synchronize task state", help="Commit message")
    args = parser.parse_args()

    task_store = TaskStore()
    deployment_agent = DeploymentAgent(task_store=task_store)

    if args.status:
        print("=== LeakeHouse MAS Runtime Status ===")
        print(f"Active Tasks: {len(task_store.tasks)}")
        for task in task_store.tasks.values():
            print(f"- [{task.state}] {task.id}: {task.title} (Assigned: {task.assigned_agent})")
        env = deployment_agent.verify_environment()
        print(f"Git Remote: {env['remote_url']} (branch: {env['branch']})")
        return

    if args.deploy:
        print("Triggering LeakeHouse Deployment Agent...")
        receipt = deployment_agent.deploy_task(commit_message=args.message)
        print(f"Deployment result: {receipt.status} (Commit: {receipt.commit_hash})")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
