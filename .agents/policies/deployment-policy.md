# Policy: Automated Git Deployment & Remote Synchronization

> [!IMPORTANT]
> **MANDATORY POLICY: PUSH TO GIT AFTER EVERY TASK IS FINISHED**
> Under no circumstances may any task transition to DONE or be reported to the user without staging, committing with conventional semantic messages, and executing `git push origin main` to `https://github.com/mohammedrehan143/Leakehouse.git`.

## 1. Principles
Every code change, feature, bug fix, or refactor executed by the LeakeHouse Multi-Agent System must be version-controlled and pushed upstream to GitHub automatically upon task completion.

- **Remote Target**: `https://github.com/mohammedrehan143/Leakehouse.git`
- **Default Branch**: `main`
- **Authorized Executor**: `deployment-agent`

## 2. Automated Triggering Rules
1. **Trigger Condition**: When `master-orchestrator` marks a task lifecycle state as `DONE`.
2. **Mandatory Post-Task Execution**: Every task completion automatically triggers `deployment-agent` to stage and push to git immediately.
2. **Quality Pre-check**:
   - `deployment-agent` verifies that Gates 1 through 4 have received positive sign-offs.
   - If tests failed or review was rejected, deployment is blocked immediately.
3. **Clean Staging**:
   - Files are staged respecting `.gitignore`.
   - Temporary artifacts, pycache, local virtualenvs, and log checkpoints are never staged.
4. **Semantic Commit Packaging**:
   - Commit message header adheres to Conventional Commits: `<type>(<scope>): <message>`.
   - The body includes the Task ID, authoring agents, and quality receipts.
5. **Direct Push Execution**:
   - Executes `git push origin main`.
   - Records the commit SHA and logs the result to `.agents/tasks/current-task.md` and `agent_runtime/.telemetry_logs/deployments.jsonl`.
6. **Failure Recovery**:
   - If a push is rejected due to remote changes, the agent fetches and attempts a clean merge/rebase.
   - If merge conflicts occur, the agent raises a critical blocker to `master-orchestrator`.
