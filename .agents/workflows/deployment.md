# Workflow: Autonomous Git Deployment

## 1. Objective
Guide the automated end-to-end process of staging, committing, verifying, and pushing verified code to GitHub (`https://github.com/mohammedrehan143/Leakehouse.git`) whenever a task transitions to `DONE`.

## 2. Sequence Diagram

```text
Master Orchestrator      Code Reviewer       Deployment Agent         GitHub Remote
         │                     │                    │                       │
         │  Task Done Check    │                    │                       │
         ├────────────────────►│                    │                       │
         │  Review Approved    │                    │                       │
         │◄────────────────────┤                    │                       │
         │                                          │                       │
         │  Invoke Deployment (Task Manifest)       │                       │
         ├─────────────────────────────────────────►│                       │
         │                                          │  1. Check Quality     │
         │                                          │  2. Git Status & Diff │
         │                                          │  3. Stage (git add)   │
         │                                          │  4. Commit            │
         │                                          │                       │
         │                                          │  git push origin main │
         │                                          ├──────────────────────►│
         │                                          │  Remote Push Success  │
         │                                          │◄──────────────────────┤
         │                                          │                       │
         │  Return Deployment Receipt (Commit SHA)  │                       │
         │◄─────────────────────────────────────────┤                       │
         ▼                                          ▼                       ▼
```

## 3. Step-by-Step Procedure

1. **Intake & Verification**:
   - `deployment-agent` receives task completion packet from `master-orchestrator`.
   - Verifies test logs and independent code reviewer approval.

2. **Index Inspection**:
   - Run `git status --porcelain` to identify changed, new, and deleted files.
   - Verify zero unwanted files (secrets, caches, binaries).

3. **Atomic Staging & Commit**:
   - Execute `git add -A`.
   - Compose commit message:
     ```
     feat(<scope>): <summary> [TASK-ID]

     - Verified by Quality Gates 1-4
     - Co-Authored-By: LeakeHouse Multi-Agent System
     ```
   - Execute `git commit -m "..."`.

4. **Push Upstream**:
   - Execute `git push origin main`.
   - Capture push output and commit SHA.

5. **Receipt Logging**:
   - Write deployment receipt to `.agents/tasks/current-task.md`.
   - Update `agent_runtime/shared/task_store.py` state to `DEPLOYED`.
