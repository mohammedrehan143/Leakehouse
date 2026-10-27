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


def test_sales_trends_endpoint():
    res = client.get("/api/v1/sales/trends")
    assert res.status_code == 200
    data = res.json()
    assert "daily" in data
    assert "monthly" in data
    assert isinstance(data["daily"], list)
    assert isinstance(data["monthly"], list)


def test_products_performance_endpoint():
    res = client.get("/api/v1/products/performance?limit=5")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_countries_performance_endpoint():
    res = client.get("/api/v1/countries/performance")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_analytics_anomalies_endpoint():
    res = client.get("/api/v1/analytics/anomalies")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_analytics_forecast_endpoint():
    res = client.get("/api/v1/analytics/forecast?horizon=7")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data


def test_data_quality_endpoint():
    res = client.get("/api/v1/data-quality")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_pipeline_runs_endpoint():
    res = client.get("/api/v1/pipeline/runs")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_agent_task_creation_and_retrieval():
    res = client.post("/api/v1/agents/tasks", json={"query": "What is our revenue?"})
    assert res.status_code == 200
    data = res.json()
    assert "task_id" in data
    task_id = data["task_id"]
    assert data["status"] == "succeeded"
    assert len(data["plan"]) > 0
    assert len(data["findings"]) > 0

    # Retrieve by task_id
    res_get = client.get(f"/api/v1/agents/tasks/{task_id}")
    assert res_get.status_code == 200
    assert res_get.json()["task_id"] == task_id

    # 404 for invalid task_id
    res_404 = client.get("/api/v1/agents/tasks/non_existent_task_id")
    assert res_404.status_code == 404
