# Interface & Schema Contracts Ledger

## 1. System Contract Overview
All cross-domain communications (FastAPI backend <-> React frontend) and data platform specifications are registered here. No frontend or backend agent may invent divergent endpoints or data fields.

---

## 2. Active Schema Contracts

### Contract: System Health & Deployment Heartbeat
- **Endpoint**: `GET /api/v1/health`
- **Producer**: `api-engineer`
- **Consumer**: `api-integration-engineer`, `devops-engineer`
- **Request Format**: None
- **Response Format**:
  ```json
  {
    "status": "healthy",
    "service": "leakehouse-core",
    "version": "0.1.0",
    "database": "connected",
    "timestamp": "2026-10-27T14:30:00Z"
  }
  ```
- **Error Codes**: `503 Service Unavailable` if database health check fails.

---

## 3. Contract Change Log
| Contract ID | Author | Status | Change Description |
| :--- | :--- | :--- | :--- |
| `CTR-001` | `software-architect` | APPROVED | Initial core health check and platform contract specification |
