# Workflow: Cross-Domain Integration & End-to-End Testing

## 1. Objective
Ensure smooth, error-free interoperation between Backend APIs and Frontend client interfaces.

## 2. Steps
1. **Contract Synchronization**:
   - `software-architect` audits `.agents/tasks/contracts.md`.
2. **Mock Server / Staging Harness**:
   - `integration-engineer` spins up mock responses or test containers.
3. **E2E Test Execution**:
   - Verify data payloads, status codes, query pagination, and WebSocket messages.
4. **Sign-off**:
   - `integration-engineer` submits Green Integration Receipt to `master-orchestrator`.
