# Workflow: Bug Fixing & Hotpatch Protocol

## 1. Objective
Ensure systematic diagnosis, root-cause identification, regression testing, and deployment for defect resolution.

## 2. Steps
1. **Reproduction & Triage**:
   - Master Orchestrator creates bug ticket with reproduction steps.
   - Assigns investigation to relevant domain orchestrator (`backend-orchestrator` or `frontend-orchestrator`).
2. **Failing Test Creation**:
   - Before writing fix code, the domain test engineer writes a failing regression test capturing the bug.
3. **Remediation**:
   - Domain engineer implements minimal, targeted fix within file boundaries.
4. **Verification**:
   - Regression test passes; full suite remains 100% green.
5. **Code Review**:
   - `independent-code-reviewer` checks fix for unintended side-effects.
6. **Deployment**:
   - `deployment-agent` commits (`fix(<scope>): ...`) and pushes to `origin/main`.
