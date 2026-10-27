# Policy: Multi-Agent Handoff & Communication Contract

## 1. Principles
All inter-agent communication within the LeakeHouse Multi-Agent System must be formal, structured, and auditable. Loose, conversational chat without explicit contracts is prohibited.

## 2. Standard Task Lifecycle States

Every task in the Task Store (`agent_runtime/shared/task_store.py`) must exist in one of the following canonical states:

```text
  ┌───────────┐
  │  BACKLOG  │
  └─────┬─────┘
        ▼
  ┌───────────┐
  │   READY   │ ◄────────────────────────┐
  └─────┬─────┘                          │
        ▼                                │
  ┌───────────┐                          │
  │IN_PROGRESS│                          │
  └─────┬─────┘                          │
        │                                │
        ├───────────────► ┌───────────┐  │
        │                 │  BLOCKED  ├──┘
        ▼                 └───────────┘
  ┌───────────┐
  │ IN_REVIEW │
  └─────┬─────┘
        │
        ├───────────────► ┌─────────────────────┐
        │                 │ VERIFICATION_FAILED ├──┐
        ▼                 └─────────────────────┘  │
  ┌───────────┐                                    │
  │   DONE    │                                    │
  └─────┬─────┘ ◄──────────────────────────────────┘
        ▼
  ┌──────────────────────┐
  │ DEPLOYED (Git Push)  │
  └──────────────────────┘
```

- **BACKLOG**: Task defined and prioritized; prerequisites pending.
- **READY**: Prerequisites satisfied, contracts defined, ready for agent pickup.
- **IN_PROGRESS**: Actively being implemented by assigned agent.
- **BLOCKED**: Implementation impeded by external dependency or unresolvable question.
- **IN_REVIEW**: Implementation complete; undergoing testing and peer audit.
- **VERIFICATION_FAILED**: Quality gate, integration test, or peer review rejected the work.
- **DONE**: All quality gates satisfied; work receipt accepted by Master Orchestrator.
- **DEPLOYED**: Changes automatically staged, committed, and pushed upstream to `https://github.com/mohammedrehan143/Leakehouse.git` by `deployment-agent`.

## 3. Mandatory 9-Point Handoff Contract Schema

Every task delegation and completion handoff must strictly contain the following 9 elements:

1. **Task ID & Objective**: Unique task identifier (e.g. `BE-TASK-101`) and explicit statement of what is to be accomplished.
2. **Scope & File Ownership**: Exact list of files and directories the receiving agent is authorized to modify.
3. **Context & Relevant Documentation**: Architectural diagrams, ADR links, and relevant schema files.
4. **Dependencies**: Upstream tasks or services that must be completed or available prior to execution.
5. **Acceptance Criteria**: Testable, binary conditions that determine task success.
6. **Files Changed**: Comprehensive manifest of all modified, created, or deleted files.
7. **Tests Executed & Actual Results**: Exact commands run, tests passed/failed count, and code coverage percentage.
8. **Blockers, Risks & Assumptions**: Identified risks, performance considerations, or unresolved questions.
9. **Recommended Next Step**: Clear instruction on which agent or stage follows next in the pipeline (e.g. invoke `deployment-agent`).
