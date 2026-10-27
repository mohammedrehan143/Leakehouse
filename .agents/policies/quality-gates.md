# Policy: Quality Gates & Verification Standards

## 1. Overview
No task, pull request, or release candidate in LeakeHouse may transition to `DONE` and be deployed without systematically passing all five Quality Gates. Quality gates are evaluated programmatically and validated by the `independent-code-reviewer`, `master-orchestrator`, and `deployment-agent`.

```text
       ┌───────────────┐
       │ Work Complete │
       └───────┬───────┘
               ▼
┌───────────────────────────────┐
│ Gate 1: Static Analysis       │ ──► [FAIL] ──► VERIFICATION_FAILED
│ (ruff, black, mypy, tsc)      │
└──────────────┬────────────────┘
               ▼ [PASS]
┌───────────────────────────────┐
│ Gate 2: Automated Testing     │ ──► [FAIL] ──► VERIFICATION_FAILED
│ (pytest, vitest, cov >= 85%)  │
└──────────────┬────────────────┘
               ▼ [PASS]
┌───────────────────────────────┐
│ Gate 3: Security & Secrets    │ ──► [FAIL] ──► BLOCKED / VERIFICATION_FAILED
│ (secrets scan, bandit, OWASP) │
└──────────────┬────────────────┘
               ▼ [PASS]
┌───────────────────────────────┐
│ Gate 4: Independent Review    │ ──► [FAIL] ──► VERIFICATION_FAILED
│ (independent-code-reviewer)   │
└──────────────┬────────────────┘
               ▼ [PASS]
┌───────────────────────────────┐
│ Gate 5: Git Deployment        │ ──► [FAIL] ──► BLOCKED
│ (deployment-agent push main)  │
└──────────────┬────────────────┘
               ▼ [PASS]
       ┌───────────────┐
       │  Status: DONE │
       └───────────────┘
```

---

## 2. Gate 1: Static Analysis & Linting
- **Python**:
  - `ruff check backend/ agent_runtime/` reports zero errors.
  - `black --check backend/ agent_runtime/` reports zero formatting diffs.
  - `mypy backend/ agent_runtime/` reports zero typing errors.
- **TypeScript**:
  - `tsc --noEmit` reports zero compile-time errors.
  - `eslint frontend/src/` reports zero errors.

## 3. Gate 2: Automated Testing & Coverage
- **Backend**:
  - `pytest backend/tests/ --cov=backend/src --cov-fail-under=85` runs with 100% assertions green and minimum 85% branch coverage.
- **Frontend**:
  - `npm --prefix frontend test` runs with 100% assertions green.
- **Agent Runtime**:
  - `pytest agent_runtime/tests/` passes with 100% green tests.

## 4. Gate 3: Security & Secrets Audit
- **Zero Secrets**: Automated scanner confirms no API keys, tokens, or plaintext credentials in diffs.
- **Static Security**: Bandit/Trivy scans report zero High or Critical vulnerabilities.
- **Input Validation**: All public endpoints enforce Pydantic/Zod schema validation.

## 5. Gate 4: Independent Peer Review
- Verification by `independent-code-reviewer` that changes comply with coding standards and file boundaries.

## 6. Gate 5: Automated Git Deployment & Remote Push
- `deployment-agent` verifies repository synchronization with `origin/main` (`https://github.com/mohammedrehan143/Leakehouse.git`).
- Stages modified/added files cleanly.
- Executes git commit with conventional semantic message.
- Executes `git push origin main`.
- Generates a verified Deployment Receipt.
