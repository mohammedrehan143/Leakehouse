# LeakeHouse Multi-Agent Architecture & Governance Guide

> [!IMPORTANT]
> **ABSOLUTE MANDATORY RULE: PUSH TO GIT AFTER EVERY TASK IS FINISHED**
> After **every single task, sub-task, or phase** is completed, the changes MUST be staged, committed with conventional semantic commit messages, and pushed directly upstream to GitHub (`https://github.com/mohammedrehan143/Leakehouse.git` on branch `main`) by the `deployment-agent`. 
> 
> **Never close a task or report completion to the user without executing an immediate Git Push.**

---

## 1. System Overview

**LeakeHouse** (housing the **RetailIQ** E-commerce Lakehouse & Analytics Platform) is engineered as an enterprise-grade platform built upon a disciplined, hierarchical **Multi-Agent System (MAS)**. Every piece of development, architecture design, testing, quality assurance, and deployment is carried out through specialized autonomous agents operating under strict protocols, explicit contracts, and mandatory quality gates.

A core operational mandate of LeakeHouse is **Autonomous Git Deployment**: every completed task is formally validated, packaged with conventional semantic commits, and pushed directly to the remote repository (`https://github.com/mohammedrehan143/Leakehouse.git`) by a dedicated **Deployment Agent**.

```
                          ┌─────────────────────────────┐
                          │     Master Orchestrator     │
                          │   (Strategic Coordinator)   │
                          └──────────────┬──────────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 ▼                       ▼                       ▼
  ┌─────────────────────────────┐ ┌──────────────────────┐ ┌─────────────────────────────┐
  │    Backend Orchestrator     │ │   Deployment Agent   │ │    Frontend Orchestrator    │
  │   (Tactical Lead - Data)    │ │(Git & Release Lead)  │ │    (Tactical Lead - Web)    │
  └──────────────┬──────────────┘ └──────────────────────┘ └──────────────┬──────────────┘
                 │                                                        │
  ┌──────────────┴──────────────┐                          ┌──────────────┴──────────────┐
  │ - Ingestion Engineer        │                          │ - UI/UX Engineer            │
  │ - Database Engineer         │                          │ - Frontend Engineer         │
  │ - ETL & Pipeline Engineer   │                          │ - Dashboard Engineer        │
  │ - dbt Engineer              │                          │ - API Integration Engineer  │
  │ - API Engineer              │                          │ - Accessibility Engineer    │
  │ - Backend Test Engineer     │                          │ - Frontend Test Engineer    │
  │ - Backend Security Engineer │                          └─────────────────────────────┘
  └─────────────────────────────┘                                         │
                 │                                                        │
                 └───────────────────────┬────────────────────────────────┘
                                         ▼
                          ┌─────────────────────────────┐
                          │   Shared Cross-Cut Squad    │
                          │ - Software Architect        │
                          │ - Integration Engineer      │
                          │ - DevOps Engineer           │
                          │ - Independent Code Reviewer │
                          └─────────────────────────────┘
```

---

## 2. Mandatory Core Directive: Push to Git After Every Task

Every task execution plan, contract, and checklist in LeakeHouse MUST include and enforce this directive:

1. **Automated Trigger**: The moment a task, sub-task, or implementation phase satisfies its acceptance criteria and tests, the `deployment-agent` is invoked immediately.
2. **Pre-Push Validation**: Confirm all tests pass (100% green), static analysis is clean, and no secrets or binaries are staged.
3. **Semantic Commit Packaging**: Generate a conventional commit (`feat(...)`, `fix(...)`, `chore(...)`) referencing the Task ID.
4. **Push Upstream**: Execute `git push origin main` to `https://github.com/mohammedrehan143/Leakehouse.git`.
5. **Deployment Receipt**: Document the commit hash, timestamp, and pushed files in the task record.
6. **Zero Lag**: No implementation is considered complete, and no agent turn ends with unpushed finished work.

---

## 3. Hierarchical Chain of Command

### 3.1 Level 0: The Master Orchestrator (`.agents/master-orchestrator.md`)
- **Authority**: Ultimate technical authority on task intake, prioritization, cross-domain arbitration, release sign-off, and deployment triggering.
- **Direct Subordinates**: Backend Orchestrator, Frontend Orchestrator, Deployment Agent, Software Architect, Independent Code Reviewer.
- **Responsibilities**:
  - Decomposes high-level epics into actionable domain work packets (`.agents/tasks/contracts.md`).
  - Assigns sub-tasks to Backend and Frontend Orchestrators.
  - Monitors state transitions in the global Task Store (`agent_runtime/shared/task_store.py`).
  - Resolves integration deadlocks between backend and frontend contracts.
  - **MANDATORY**: Triggers the `deployment-agent` upon task completion to push changes upstream to GitHub immediately.

### 3.2 Level 1: Domain Orchestrators & Deployment Lead

#### A. Backend Orchestrator (`.agents/orchestrators/backend-orchestrator.md`)
- **Authority**: Direct manager of backend services, data pipelines, database storage, schemas, APIs, and security.
- **Direct Subordinates**: Ingestion Engineer, Database Engineer, ETL Engineer, dbt Engineer, API Engineer, Backend Test Engineer, Backend Security Engineer.

#### B. Frontend Orchestrator (`.agents/orchestrators/frontend-orchestrator.md`)
- **Authority**: Direct manager of client user interfaces, web applications, dashboards, state management, and accessibility.
- **Direct Subordinates**: UI/UX Engineer, Frontend Engineer, Dashboard Engineer, API Integration Engineer, Accessibility Engineer, Frontend Test Engineer.

#### C. Deployment Agent (`.agents/shared/deployment-agent.md`)
- **Authority**: Dedicated release, version control, and remote synchronization lead.
- **Target Repository**: `https://github.com/mohammedrehan143/Leakehouse.git` (branch: `main`).
- **Trigger**: **Every time any task, subtask, or phase is completed.**
- **Responsibilities**:
  - Verifies all quality gates have passed.
  - Inspects file modifications and stages files cleanly.
  - Generates conventional commits (`feat: ...`, `fix: ...`, `chore: ...`).
  - Pushes commits to `origin/main` automatically.
  - Logs deployment receipts and verification records.

### 3.3 Level 2: Specialized Engineering Agents
Every specialized agent operates strictly within its designated file boundaries and domain scope. Cross-domain alterations without orchestrator delegation are prohibited.

---

## 4. Agent Roster & Domain Matrix

| Agent Identifier | Category | File Authority / Scope | Primary Responsibilities |
| :--- | :--- | :--- | :--- |
| `master-orchestrator` | Executive | `.agents/tasks/*`, `agent_runtime/master/*` | Epic decomposition, cross-team sync, release sign-off |
| `deployment-agent` | Deployment | Git remotes, branches, release artifacts | **Automated commits, push to git after every task** |
| `backend-orchestrator` | Domain Lead | `backend/*`, `src/retailiq/*`, `agent_runtime/backend/*` | Backend squad work distribution, pipeline validation |
| `frontend-orchestrator`| Domain Lead | `frontend/*`, `dashboard/*`, `agent_runtime/frontend/*` | Frontend squad work distribution, UI validation |
| `api-engineer` | Backend | `backend/app/api/*`, `src/retailiq/api/*` | FastAPI / REST routes, OpenAPI schemas, validation |
| `ingestion-engineer` | Backend | `src/retailiq/ingestion/*` | Dataset loading, raw schema validation, Bronze Parquet |
| `database-engineer` | Backend | `src/retailiq/database/*`, migrations | Relational schema, migrations, connection pools |
| `pipeline-engineer` | Backend | `src/retailiq/pipeline/*`, transformations | Pipeline runner, Silver cleaning, quarantine, orchestrators |
| `backend-test-engineer`| Backend | `tests/*` | Pytest fixtures, unit/mock/integration test suites |
| `backend-security-engineer`| Backend | Security policies, auth middleware | OWASP auditing, secrets protection, token validation |
| `ui-ux-engineer` | Frontend | `frontend/src/components/design-system/*` | Design systems, color tokens, typography primitives |
| `frontend-engineer` | Frontend | `frontend/src/components/*`, `frontend/src/App.tsx` | React / Streamlit component trees, layout structure |
| `dashboard-engineer` | Frontend | `dashboard/*`, `frontend/src/pages/*` | Visualizations, interactive charts, telemetry views |
| `api-integration-engineer`| Frontend | `frontend/src/services/*`, client hooks | API clients, React Query, WebSocket consumers |
| `accessibility-engineer` | Frontend | A11y tests, ARIA tags, contrast tokens | WCAG 2.1 AA compliance, keyboard navigation |
| `frontend-test-engineer`| Frontend | `frontend/tests/*`, `*.test.tsx` | Vitest, React Testing Library, UI test suites |
| `software-architect` | Shared | System architecture, schema contracts, ADRs | End-to-end design, data integrity, architecture review |
| `integration-engineer` | Shared | Cross-domain E2E testing, API contracts | Backend-Frontend bridge, mocking, smoke testing |
| `devops-engineer` | Shared | `docker-compose.yml`, `Makefile`, CI/CD | Container orchestration, Dockerfiles, environment isolation |
| `independent-code-reviewer`| Shared | All pull requests & file diffs | Objective code review, linting, complexity checks |

---

## 5. Communication & Delegation Protocol

1. **Top-Down Delegation**:
   - Master Orchestrator creates task record in `.agents/tasks/current-task.md`.
   - Domain Orchestrators decompose tasks into sub-tasks and generate Agent Execution Tickets.
   - Engineering Agents execute within strict file boundaries.

2. **Bottom-Up Reporting**:
   - Engineering Agents submit an Execution Receipt containing modified files and test passes.
   - Domain Orchestrators validate and report completion to Master Orchestrator.

3. **Mandatory Post-Task Git Push Loop**:
   - The moment any task transitions to `DONE`, Master Orchestrator invokes `deployment-agent`.
   - `deployment-agent` runs pre-push sanity checks, commits changes, and pushes directly to `https://github.com/mohammedrehan143/Leakehouse.git`.

---

## 6. Mandatory Quality Gates

No task may transition to `DONE` and be deployed without passing all 5 Quality Gates:

1. **Gate 1: Static Analysis & Linting** (Ruff, Black, ESLint, TypeScript).
2. **Gate 2: Automated Testing** (Unit & integration test suites passing with high coverage).
3. **Gate 3: Security & Secrets Audit** (Zero hardcoded secrets, zero High/Critical vulnerabilities).
4. **Gate 4: Independent Peer Review** (Sign-off from `independent-code-reviewer`).
5. **Gate 5: Automated Git Deployment** (Staged, committed, and pushed to `origin/main` by `deployment-agent`).

---

## 7. Directory Layout & Artifact Map

```
leakehouse/
├── AGENTS.md                  # Master governance document & Git Push mandate
├── README.md                  # Developer & architecture onboarding
├── .gitignore                 # Version control exclusions
├── .env.example               # Environment variables template
├── configs/                   # Settings and dataset provenance
│
├── .agents/                   # Agent Personas, Policies, Workflows
│   ├── master-orchestrator.md # L0 Coordinator
│   ├── orchestrators/         # L1 Domain Leads
│   ├── backend/               # L2 Backend Engineers
│   ├── frontend/              # L2 Frontend Engineers
│   ├── shared/                # Cross-Cutting Specialists & Deployment Agent
│   ├── workflows/             # Standard Operating Procedures & Deployment
│   ├── policies/              # Governance & Quality Policies
│   └── tasks/                 # Current Ledger & Interface Contracts
│
├── agent_runtime/             # Programmatic Python Orchestration & Deployment Engine
│   ├── master/                # Master state router
│   ├── backend/               # Backend sub-graph
│   ├── frontend/              # Frontend sub-graph
│   ├── shared/                # State store, permissions, 9-point contract
│   ├── tools/                 # Execution tools (git, fs, test)
│   └── deployment/            # Automated Git Deployment Engine & CLI
│
├── src/retailiq/              # RetailIQ Lakehouse & Ingestion Source Code
│   ├── config.py              # Configuration manager
│   ├── cli.py                 # Lakehouse CLI commands
│   ├── ingestion/             # Download, raw validation, batch manager, Bronze loader
│   ├── transformations/       # Silver cleaning & quarantine (Phase 2)
│   ├── database/              # PostgreSQL & SQLite repositories (Phase 2)
│   └── analytics/             # Business metrics & forecasting (Phase 3+)
│
├── tests/                     # Automated Test Suites (unit, integration, e2e)
├── data/                      # Lakehouse data directory (raw, processed, quarantine)
└── dashboard/                 # Streamlit analytics application (Phase 7)
```
