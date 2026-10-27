"""Unit tests for FastAPI endpoints."""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "retailiq-backend"


def test_api_v1_health():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"


def test_overview_endpoint():
    res = client.get("/api/v1/overview")
    assert res.status_code == 200
    data = res.json()
    assert "sales" in data
    assert "customers" in data


def test_agent_task_creation():
    res = client.post("/api/v1/agents/tasks", json={"query": "What is our revenue?"})
    assert res.status_code == 200
    data = res.json()
    assert "task_id" in data
    assert data["status"] == "succeeded"
    assert len(data["plan"]) > 0
    assert len(data["findings"]) > 0
