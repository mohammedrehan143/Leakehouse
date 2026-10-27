"""Hierarchical Master Agent Orchestrator.

Coordinates user queries, planning, specialist routing, controlled tool execution,
and evidence-backed synthesis.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from retailiq.agents.state import AgentTaskState, TaskExecutionStatus, ToolCallRecord
from retailiq.agents.tools import (
    query_customer_overview,
    query_data_quality_report,
    query_sales_summary,
    query_top_products,
)


class MasterAgentOrchestrator:
    """Master Orchestrator coordinating specialized intelligence agents."""

    def __init__(self) -> None:
        pass

    def execute_investigation(self, user_query: str) -> AgentTaskState:
        """Execute structured investigation pipeline: Plan -> Route -> Execute Tools -> Synthesize."""
        task_id = f"TASK_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        state = AgentTaskState(
            task_id=task_id,
            user_query=user_query,
            status=TaskExecutionStatus.RUNNING,
        )

        query_lower = user_query.lower()

        # Step 1: Routing & Planning
        if any(w in query_lower for w in ["product", "item", "stock", "bestseller"]):
            state.assigned_specialist = "ProductAnalyticsSpecialist"
            state.plan = [
                "1. Route query to Product Analytics Specialist",
                "2. Execute query_top_products tool to retrieve revenue and unit volume",
                "3. Compute revenue concentration among top items",
                "4. Synthesize findings and actionable recommendations",
            ]
            self._investigate_products(state)

        elif any(w in query_lower for w in ["customer", "repeat", "retention", "loyalty"]):
            state.assigned_specialist = "CustomerAnalyticsSpecialist"
            state.plan = [
                "1. Route query to Customer Analytics Specialist",
                "2. Execute query_customer_overview to evaluate repeat purchase metrics",
                "3. Analyze customer order distributions and guest checkout patterns",
                "4. Synthesize findings and retention recommendations",
            ]
            self._investigate_customers(state)

        elif any(w in query_lower for w in ["quality", "health", "pipeline", "quarantine", "error"]):
            state.assigned_specialist = "DataQualitySpecialist"
            state.plan = [
                "1. Route query to Data Quality Specialist",
                "2. Query automated audit table mart_data_quality",
                "3. Analyze quarantine rates and invariant violations",
                "4. Produce evidence-backed data reliability assessment",
            ]
            self._investigate_quality(state)

        else:
            # Default to Executive Revenue & Sales Specialist
            state.assigned_specialist = "ExecutiveSalesSpecialist"
            state.plan = [
                "1. Route query to Executive Sales Specialist",
                "2. Execute query_sales_summary from Gold daily and monthly marts",
                "3. Compute gross vs. net revenue considering cancellations",
                "4. Deliver executive findings and growth insights",
            ]
            self._investigate_sales(state)

        state.status = TaskExecutionStatus.SUCCEEDED
        state.updated_at = datetime.now(UTC).isoformat()
        return state

    def _investigate_sales(self, state: AgentTaskState) -> None:
        t_start = datetime.now(UTC)
        data = query_sales_summary()
        duration = (datetime.now(UTC) - t_start).total_seconds() * 1000

        state.tool_history.append(
            ToolCallRecord(
                tool_name="query_sales_summary",
                arguments={},
                output=data,
                duration_ms=round(duration, 2),
            )
        )
        state.evidence["sales_summary"] = data

        if data.get("status") == "SUCCESS":
            gross = data["gross_revenue"]
            net = data["net_revenue"]
            returns = data["returns_revenue"]
            orders = data["total_orders"]
            units = data["units_sold"]

            state.findings = [
                f"Gross revenue across recorded transactions stands at £{gross:,.2f}.",
                f"Documented returns and cancellations total £{returns:,.2f}, resulting in net revenue of £{net:,.2f}.",
                f"A total of {orders:,} unique orders were processed comprising {units:,} individual units sold.",
            ]
            state.recommendations = [
                "Track daily cancellation spikes to identify potential warehouse or fulfillment bottlenecks.",
                "Implement proactive customer notifications during return windows to minimize post-purchase dissatisfaction.",
            ]
        else:
            state.findings = ["No sales data currently loaded in Gold marts. Run pipeline to populate data."]
            state.recommendations = ["Execute 'python -m retailiq.cli run-all' to refresh data lakehouse."]

    def _investigate_products(self, state: AgentTaskState) -> None:
        t_start = datetime.now(UTC)
        products = query_top_products(limit=5)
        duration = (datetime.now(UTC) - t_start).total_seconds() * 1000

        state.tool_history.append(
            ToolCallRecord(
                tool_name="query_top_products",
                arguments={"limit": 5},
                output=products,
                duration_ms=round(duration, 2),
            )
        )
        state.evidence["top_products"] = products

        if products:
            top_item = products[0]
            state.findings = [
                f"Top revenue generator is StockCode '{top_item['stock_code']}' ({top_item['description']}) with £{top_item['total_revenue']:,.2f} in sales across {top_item['total_units_sold']:,} units.",
                f"Identified {len(products)} leading product lines driving high-volume sales velocity.",
            ]
            state.recommendations = [
                "Ensure safety inventory levels for top 5 SKUs to prevent stockouts.",
                "Bundle lower-velocity accessories with top-performing product lines to increase average order values.",
            ]
        else:
            state.findings = ["No product performance records found in Gold marts."]
            state.recommendations = ["Ingest and transform transactions to build product performance views."]

    def _investigate_customers(self, state: AgentTaskState) -> None:
        t_start = datetime.now(UTC)
        data = query_customer_overview()
        duration = (datetime.now(UTC) - t_start).total_seconds() * 1000

        state.tool_history.append(
            ToolCallRecord(
                tool_name="query_customer_overview",
                arguments={},
                output=data,
                duration_ms=round(duration, 2),
            )
        )
        state.evidence["customer_overview"] = data

        if data.get("status") == "SUCCESS":
            reg = data["total_registered_customers"]
            repeat = data["repeat_customers"]
            rate = data["repeat_purchase_rate_pct"]
            avg_spend = data["average_customer_spend"]

            state.findings = [
                f"The platform tracks {reg:,} registered customers, of which {repeat:,} ({rate:.1f}%) are repeat purchasers.",
                f"Average spend per registered customer is £{avg_spend:,.2f}.",
            ]
            state.recommendations = [
                "Establish automated email re-engagement for customers approaching the 60-day inactivity threshold.",
                "Provide incentive discounts for guest checkouts to register an account, boosting attribution.",
            ]
        else:
            state.findings = ["Customer dimensional data is not yet computed."]
            state.recommendations = ["Run the lakehouse pipeline to populate customer metrics."]

    def _investigate_quality(self, state: AgentTaskState) -> None:
        t_start = datetime.now(UTC)
        checks = query_data_quality_report()
        duration = (datetime.now(UTC) - t_start).total_seconds() * 1000

        state.tool_history.append(
            ToolCallRecord(
                tool_name="query_data_quality_report",
                arguments={},
                output=checks,
                duration_ms=round(duration, 2),
            )
        )
        state.evidence["quality_report"] = checks

        if checks:
            passes = sum(1 for c in checks if c["status"] == "PASS")
            fails = sum(1 for c in checks if c["status"] == "FAIL")
            state.findings = [
                f"Data quality audit verified {len(checks)} critical invariants: {passes} passed, {fails} failed.",
                "Quarantine isolation actively intercepts and prevents zero/negative pricing records from corrupting reporting.",
            ]
            state.recommendations = [
                "Review quarantined items periodically to detect any changes in upstream POS export formats.",
            ]
        else:
            state.findings = ["No recent data quality execution logs found."]
            state.recommendations = ["Execute 'python -m retailiq.cli run-all' to generate fresh quality telemetry."]
