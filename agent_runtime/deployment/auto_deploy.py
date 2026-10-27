"""CLI entrypoint for the LeakeHouse Automated Git Deployment Agent.

Usage:
    python -m agent_runtime.deployment.auto_deploy --message "feat(core): implement feature" --task-id "TASK-101"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agent_runtime.deployment.deployment_agent import DeploymentAgent


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LeakeHouse Automated Git Deployment: Commit & Push to GitHub on Task Completion."
    )
    parser.add_argument(
        "-m",
        "--message",
        type=str,
        default=None,
        help="Commit message following Conventional Commits standard",
    )
    parser.add_argument(
        "-t",
        "--task-id",
        type=str,
        default=None,
        help="Optional Task ID (e.g. TASK-101)",
    )
    parser.add_argument(
        "--branch",
        type=str,
        default="main",
        help="Target git branch (default: main)",
    )
    parser.add_argument(
        "--remote",
        type=str,
        default="origin",
        help="Target git remote (default: origin)",
    )
    args = parser.parse_args()

    agent = DeploymentAgent()
    env = agent.verify_environment()
    print(f"[*] Deployment Agent active for repository: {env['remote_url']}")
    print(f"[*] Branch: {env['branch']}")

    try:
        receipt = agent.deploy_task(
            task_id=args.task_id,
            commit_message=args.message,
            remote=args.remote,
            branch=args.branch,
        )
        print(f"[+] Deployment complete! Status: {receipt.status}")
        print(f"[+] Commit Hash: {receipt.commit_hash}")
        print(f"[+] Message: {receipt.commit_message}")
        print(f"[+] Files: {len(receipt.files_pushed)} files staged and pushed")
        if receipt.details.get("push_output"):
            print(f"[+] Push Output: {receipt.details['push_output']}")
    except Exception as e:
        print(f"[!] Deployment failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
