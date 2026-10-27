"""FastAPI Backend Application for RetailIQ.

Designed for high-performance REST APIs and seamless deployment on Render.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from retailiq.agents.orchestrator import MasterAgentOrchestrator
from retailiq.agents.state import AgentTaskState
from retailiq.agents.tools import (
    query_customer_overview,
    query_data_quality_report,
    query_sales_summary,
    query_top_products,
)
from retailiq.config import settings
from retailiq.database.connection import get_session, init_db
from retailiq.database.models import (
    MartCountryPerformance,
    MartCustomerMetrics,
    MartDailySales,
    MartMonthlySales,
    MartProductPerformance,
    PipelineRunRecord,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and seed baseline data if needed on startup."""
    init_db()
    yield


app = FastAPI(
    title="RetailIQ Analytics & AI Agent API",
    description="Backend API powering the RetailIQ Lakehouse & Multi-Agent Intelligence Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Middleware (supports local development and Vercel domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_agent_orchestrator = MasterAgentOrchestrator()
_tasks_cache: dict[str, AgentTaskState] = {}


# -----------------------------------------------------------------------------
# Health Check Endpoints (Render requirement)
# -----------------------------------------------------------------------------


@app.get("/health")
@app.get("/api/v1/health")
def health_check() -> dict[str, Any]:
    """Health status endpoint for uptime monitors and Render deployment checks."""
    return {
        "status": "healthy",
        "service": "retailiq-backend",
        "version": "0.1.0",
        "environment": os.environ.get("RETAILIQ_ENV", "production"),
    }


# -----------------------------------------------------------------------------
# Analytics & Metrics Endpoints
# -----------------------------------------------------------------------------


@app.get("/api/v1/overview")
def get_executive_overview() -> dict[str, Any]:
    """Retrieve high-level business KPIs."""
    summary = query_sales_summary()
    customer_info = query_customer_overview()
    return {
        "sales": summary,
        "customers": customer_info,
    }


@app.get("/api/v1/sales/trends")
def get_sales_trends() -> dict[str, Any]:
    """Retrieve daily and monthly sales trend time-series."""
    with get_session() as session:
        daily = (
            session.query(MartDailySales)
            .order_by(MartDailySales.date_key.asc())
            .all()
        )
        monthly = (
            session.query(MartMonthlySales)
            .order_by(MartMonthlySales.year_month.asc())
            .all()
        )

        return {
            "daily": [
                {
                    "date": r.date_key,
                    "gross_revenue": r.gross_revenue,
                    "returns_revenue": r.returns_revenue,
                    "net_revenue": r.net_revenue,
                    "order_count": r.order_count,
                    "units_sold": r.units_sold,
                }
                for r in daily
            ],
            "monthly": [
                {
                    "month": r.year_month,
                    "gross_revenue": r.gross_revenue,
                    "returns_revenue": r.returns_revenue,
                    "net_revenue": r.net_revenue,
                    "order_count": r.order_count,
                    "unique_customers": r.unique_customers,
                }
                for r in monthly
            ],
        }


@app.get("/api/v1/products/performance")
def get_products_performance(limit: int = Query(default=10, ge=1, le=100)) -> list[dict[str, Any]]:
    """Retrieve top performing products."""
    return query_top_products(limit=limit)


@app.get("/api/v1/countries/performance")
def get_countries_performance() -> list[dict[str, Any]]:
    """Retrieve revenue and order counts broken down by country."""
    with get_session() as session:
        records = (
            session.query(MartCountryPerformance)
            .order_by(MartCountryPerformance.total_revenue.desc())
            .all()
        )
        return [
            {
                "country": r.country,
                "total_revenue": r.total_revenue,
                "order_count": r.order_count,
                "unique_customers": r.unique_customers,
            }
            for r in records
        ]


@app.get("/api/v1/data-quality")
def get_data_quality_report() -> list[dict[str, Any]]:
    """Retrieve audit records of automated data quality checks."""
    return query_data_quality_report()


@app.get("/api/v1/pipeline/runs")
def get_pipeline_runs() -> list[dict[str, Any]]:
    """Retrieve execution history of lakehouse pipeline runs."""
    with get_session() as session:
        runs = (
            session.query(PipelineRunRecord)
            .order_by(PipelineRunRecord.started_at.desc())
            .limit(10)
            .all()
        )
        return [
            {
                "run_id": r.run_id,
                "pipeline_name": r.pipeline_name,
                "status": r.status,
                "started_at": r.started_at.isoformat(),
                "duration_seconds": r.duration_seconds,
            }
            for r in runs
        ]


# -----------------------------------------------------------------------------
# AI Agent Console Endpoints
# -----------------------------------------------------------------------------


class AgentInvestigationRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500, description="Natural language investigation prompt")


@app.post("/api/v1/agents/tasks")
def create_agent_task(payload: AgentInvestigationRequest) -> AgentTaskState:
    """Submit a question or investigation prompt to the Multi-Agent System."""
    state = _agent_orchestrator.execute_investigation(payload.query)
    _tasks_cache[state.task_id] = state
    return state


@app.get("/api/v1/agents/tasks/{task_id}")
def get_agent_task(task_id: str) -> AgentTaskState:
    """Retrieve state and evidence from an agent investigation."""
    state = _tasks_cache.get(task_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return state
