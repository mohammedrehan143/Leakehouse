# Workflow: Feature Development Lifecycle

## 1. Objective
Define the structured process for implementing new features from PRD ingestion to Git deployment.

## 2. Process Stages

### Stage 1: Intake & Epic Decomposition
1. `master-orchestrator` digests user feature request.
2. Formulates high-level ticket in `.agents/tasks/current-task.md`.
3. Requests `software-architect` to specify or update API/data contracts in `.agents/tasks/contracts.md`.

### Stage 2: Contract-First Domain Execution
1. **Backend Wave**:
   - `backend-orchestrator` assigns subtasks: models & storage -> ingestion & pipeline -> API routes.
   - `backend-test-engineer` and `backend-security-engineer` run verification.
2. **Frontend Wave**:
   - `frontend-orchestrator` assigns subtasks: design system -> components -> dashboard views -> client tests.
   - `accessibility-engineer` and `frontend-test-engineer` validate UI.

### Stage 3: Cross-Domain Integration
1. `integration-engineer` executes end-to-end tests against contracts.
2. If discrepancies arise, contracts are revised with `software-architect`.

### Stage 4: Quality Gate Audit & Peer Review
1. Automated linters, type checks, and security scans run.
2. `independent-code-reviewer` performs unbiased review and issues sign-off.

### Stage 5: Autonomous Deployment
1. `deployment-agent` commits and pushes changes to `https://github.com/mohammedrehan143/Leakehouse.git`.
2. Master Orchestrator outputs final Executive Report.
