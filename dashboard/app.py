"""RetailIQ Streamlit Data Lakehouse & Multi-Agent Analytics Application."""

import streamlit as st
import pandas as pd
from retailiq.database.connection import get_session
from retailiq.database.models import (
    MartDailySales,
    MartMonthlySales,
    MartProductPerformance,
    MartCustomerMetrics,
    MartCountryPerformance,
    MartDataQuality,
)
from retailiq.agents.orchestrator import MasterAgentOrchestrator

st.set_page_config(
    page_title="RetailIQ Lakehouse & Multi-Agent Analytics",
    page_icon="🛍️",
    layout="wide",
)

st.title("🛍️ RetailIQ — E-commerce Data Lakehouse & AI Agent Console")
st.markdown("Production-grade Bronze–Silver–Gold Lakehouse analytics with an autonomous Multi-Agent AI layer.")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Overview",
    "📦 Product Intelligence",
    "👥 Customer Analytics",
    "🛡️ Data Quality",
    "🤖 AI Agent Console",
])

with tab1:
    st.subheader("Executive Overview (Verified Gold Marts)")
    with get_session() as session:
        daily_records = session.query(MartDailySales).all()
        if daily_records:
            total_gross = sum(r.gross_revenue for r in daily_records)
            total_net = sum(r.net_revenue for r in daily_records)
            total_returns = sum(r.returns_revenue for r in daily_records)
            total_orders = sum(r.order_count for r in daily_records)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Gross Revenue", f"£{total_gross:,.2f}")
            c2.metric("Net Revenue", f"£{total_net:,.2f}")
            c3.metric("Returns / Cancellations", f"£{total_returns:,.2f}")
            c4.metric("Total Orders", f"{total_orders:,}")

            df_daily = pd.DataFrame([{
                "Date": r.date_key,
                "Gross Revenue": r.gross_revenue,
                "Net Revenue": r.net_revenue,
                "Orders": r.order_count,
            } for r in daily_records])
            st.line_chart(df_daily.set_index("Date")[["Gross Revenue", "Net Revenue"]])
        else:
            st.info("No sales records loaded. Run 'python -m retailiq.cli run-all' to populate.")

with tab2:
    st.subheader("Top Products by Revenue")
    with get_session() as session:
        prods = session.query(MartProductPerformance).order_by(MartProductPerformance.total_revenue.desc()).limit(15).all()
        if prods:
            df_prod = pd.DataFrame([{
                "StockCode": p.stock_code,
                "Description": p.description,
                "Revenue (£)": p.total_revenue,
                "Units Sold": p.total_units_sold,
                "Orders": p.order_count,
            } for p in prods])
            st.dataframe(df_prod, use_container_width=True)
        else:
            st.info("Product performance mart is empty.")

with tab3:
    st.subheader("Customer Intelligence & Repeat Rates")
    with get_session() as session:
        custs = session.query(MartCustomerMetrics).all()
        if custs:
            repeats = sum(1 for c in custs if c.is_repeat_purchaser)
            pct = (repeats / len(custs) * 100) if custs else 0
            st.metric("Repeat Purchaser Rate", f"{pct:.1f}%", f"{repeats} of {len(custs)} customers")
        else:
            st.info("Customer metrics not yet built.")

with tab4:
    st.subheader("Data Quality Invariant Checks")
    with get_session() as session:
        q_checks = session.query(MartDataQuality).all()
        if q_checks:
            df_q = pd.DataFrame([{
                "Check": q.check_name,
                "Status": q.status,
                "Severity": q.severity,
                "Examined": q.records_examined,
                "Failed": q.records_failed,
                "Details": q.details,
            } for q in q_checks])
            st.dataframe(df_q, use_container_width=True)
        else:
            st.info("No quality check records logged.")

with tab5:
    st.subheader("🤖 AI Agent Investigation Interface")
    query = st.text_input("Ask an investigation question:", "What are our top bestselling products?")
    if st.button("Submit to Agent Plane"):
        orch = MasterAgentOrchestrator()
        with st.spinner("Agent planning and executing tools..."):
            state = orch.execute_investigation(query)
            st.success(f"Assigned Specialist: {state.assigned_specialist}")
            st.markdown("### Execution Plan")
            for step in state.plan:
                st.write(step)
            st.markdown("### Verified Findings")
            for f in state.findings:
                st.markdown(f"- {f}")
            st.markdown("### Strategic Recommendations")
            for r in state.recommendations:
                st.markdown(f"- {r}")
