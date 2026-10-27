# LeakeHouse

> Enterprise-grade platform engineered with an autonomous, hierarchical **Multi-Agent System (MAS)** and continuous automated Git deployment.

---

## 🏛️ Multi-Agent Architecture

LeakeHouse operates under a strictly governed hierarchical multi-agent structure:

- **Level 0 (Supreme Executive & Strategic Coordinator)**: `master-orchestrator`
- **Level 1 (Domain Tactical Leads)**:
  - `backend-orchestrator` (Data, services, ingestion, storage)
  - `frontend-orchestrator` (Web UI, dashboard, user interactions)
  - `deployment-agent` (Autonomous git staging, semantic commits, remote push)
- **Level 2 (Specialized Engineering Agents)**:
  - Backend: `api-engineer`, `database-engineer`, `ingestion-engineer`, `pipeline-engineer`, `backend-test-engineer`, `backend-security-engineer`
  - Frontend: `ui-ux-engineer`, `frontend-engineer`, `dashboard-engineer`, `api-integration-engineer`, `accessibility-engineer`, `frontend-test-engineer`
- **Cross-Cut Shared Squad**:
  - `software-architect` (Architecture decision records, schema contracts)
  - `integration-engineer` (End-to-end integration and smoke verification)
  - `devops-engineer` (Docker, environment configurations, CI/CD)
  - `independent-code-reviewer` (Unbiased code quality and security gatekeeper)

For the comprehensive governance specification, see [AGENTS.md](AGENTS.md).

---

## 🚀 Autonomous Git Deployment Agent

A core capability of LeakeHouse is the **Deployment Agent** (`deployment-agent`):
- **Remote**: `https://github.com/mohammedrehan143/Leakehouse.git`
- **Branch**: `main`
- **Mandate**: Every time a task or epic is validated and transitions to `DONE`, changes are staged, packaged into Conventional Commits, pushed upstream to GitHub, and recorded with an auditable Deployment Receipt.

### Manual or Programmatic Trigger
```bash
# Via Python module CLI
python -m agent_runtime.deployment.auto_deploy --message "feat(core): implement new feature" --task-id "TASK-101"

# Via Runtime Entrypoint
python -m agent_runtime.main --deploy --message "feat: sync changes"
```

---

## 🛡️ Mandatory Quality Gates

Every task must satisfy all 5 Quality Gates before deployment:
1. **Gate 1**: Static Analysis & Linting (Ruff, Black, ESLint, TypeScript)
2. **Gate 2**: Automated Testing (Pytest, Vitest, >= 85% branch coverage)
3. **Gate 3**: Security & Secrets Audit (Zero hardcoded secrets, OWASP compliance)
4. **Gate 4**: Independent Peer Review (`independent-code-reviewer` approval)
5. **Gate 5**: Automated Git Deployment (`deployment-agent` remote push)

---

## 📁 Repository Structure

```
leakehouse/
├── AGENTS.md                  # Master MAS governance manual
├── README.md                  # Project overview and quickstart
├── .gitignore                 # Version control rules
│
├── .agents/                   # Personas, policies, workflows & task ledger
│   ├── master-orchestrator.md # L0 Supreme Executive
│   ├── orchestrators/         # L1 Tactical domain leads
│   ├── backend/               # L2 Backend engineers
│   ├── frontend/              # L2 Frontend engineers
│   ├── shared/                # Cross-cutting specialists & deployment-agent
│   ├── workflows/             # Standard operating procedures
│   ├── policies/              # Coding standards, ownership, quality gates
│   └── tasks/                 # Current task ledger & contracts
│
├── agent_runtime/             # Programmatic Python execution engine
│   ├── deployment/            # Automated Git deployment agent & CLI
│   ├── shared/                # Task store, state machine, permissions
│   ├── tools/                 # Git, filesystem, and test execution tools
│   ├── tests/                 # Runtime unit tests
│   └── main.py                # Agent runtime entrypoint
│
├── backend/                   # Backend services (FastAPI, storage, pipelines)
└── frontend/                  # Frontend web applications (React, Vite)
```
