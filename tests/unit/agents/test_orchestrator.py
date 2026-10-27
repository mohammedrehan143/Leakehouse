"""Unit tests for MasterAgentOrchestrator."""

from retailiq.agents.orchestrator import MasterAgentOrchestrator
from retailiq.agents.state import TaskExecutionStatus


def test_agent_orchestrator_sales_routing():
    orchestrator = MasterAgentOrchestrator()
    state = orchestrator.execute_investigation("What is our total revenue and sales trends?")

    assert state.status == TaskExecutionStatus.SUCCEEDED
    assert state.assigned_specialist == "ExecutiveSalesSpecialist"
    assert len(state.plan) > 0
    assert len(state.tool_history) > 0
    assert state.tool_history[0].tool_name == "query_sales_summary"


def test_agent_orchestrator_product_routing():
    orchestrator = MasterAgentOrchestrator()
    state = orchestrator.execute_investigation("Which product is our top bestseller?")

    assert state.status == TaskExecutionStatus.SUCCEEDED
    assert state.assigned_specialist == "ProductAnalyticsSpecialist"
    assert state.tool_history[0].tool_name == "query_top_products"


def test_agent_orchestrator_customer_routing():
    orchestrator = MasterAgentOrchestrator()
    state = orchestrator.execute_investigation("What is the repeat customer purchase rate?")

    assert state.status == TaskExecutionStatus.SUCCEEDED
    assert state.assigned_specialist == "CustomerAnalyticsSpecialist"
    assert state.tool_history[0].tool_name == "query_customer_overview"


def test_agent_orchestrator_quality_routing():
    orchestrator = MasterAgentOrchestrator()
    state = orchestrator.execute_investigation("Is the data pipeline healthy and are there quality errors?")

    assert state.status == TaskExecutionStatus.SUCCEEDED
    assert state.assigned_specialist == "DataQualitySpecialist"
    assert state.tool_history[0].tool_name == "query_data_quality_report"
