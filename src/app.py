import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Cloud Cost Optimization Dashboard",
    layout="wide"
)

st.title("☁️ Cloud Cost Optimization Dashboard")

# ---------------------------
# Load Data (SAFE)
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/cloud_cost.csv")

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
        format="mixed"
    )

    df = df.dropna(subset=["date"])
    df["cost_usd"] = pd.to_numeric(df["cost_usd"], errors="coerce").fillna(0)

    return df

df = load_data()

# ---------------------------
# REAL Cost Calculations
# ---------------------------
total_cost = df["cost_usd"].sum()

# Idle cost calculation (data-driven)
idle_cost = 0

for service, s_df in df.groupby("service"):
    peak = s_df["cost_usd"].max()
    idle_threshold = peak * 0.8
    idle_cost += s_df[s_df["cost_usd"] < idle_threshold]["cost_usd"].sum()

used_cost = total_cost - idle_cost

# FinOps Score (real)
idle_ratio = idle_cost / total_cost if total_cost > 0 else 0

if idle_ratio < 0.15:
    finops_score = 5
elif idle_ratio < 0.25:
    finops_score = 4
elif idle_ratio < 0.35:
    finops_score = 3
elif idle_ratio < 0.5:
    finops_score = 2
else:
    finops_score = 1

# ---------------------------
# KPI Section
# ---------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("💰 Total Cost", f"${total_cost:,.2f}")
c2.metric("✅ Used Cost", f"${used_cost:,.2f}")
c3.metric("⚠️ Idle Cost", f"${idle_cost:,.2f}")
c4.metric("⭐ FinOps Score", f"{finops_score}/5")

# ---------------------------
# Monthly Trend
# ---------------------------
trend = (
    df.groupby(pd.Grouper(key="date", freq="M"))["cost_usd"]
    .sum()
    .reset_index()
)

fig_trend = px.line(
    trend,
    x="date",
    y="cost_usd",
    title="📈 Monthly Cloud Cost Trend",
    markers=True
)

fig_trend.update_layout(dragmode=False)
st.plotly_chart(fig_trend, use_container_width=True)

# ---------------------------
# Used vs Idle Chart
# ---------------------------
usage_df = pd.DataFrame({
    "Type": ["Used Cost", "Idle Cost"],
    "Cost": [used_cost, idle_cost]
})

fig_usage = px.pie(
    usage_df,
    names="Type",
    values="Cost",
    title="⚙️ Used vs Idle Cost Distribution"
)

fig_usage.update_layout(dragmode=False)
st.plotly_chart(fig_usage, use_container_width=True)

# ---------------------------
# AI-Based Insights
# ---------------------------
st.subheader("🧠 AI-Based Cost Optimization Insights")

if idle_ratio > 0.3:
    st.warning("🔻 High idle cost detected. Rightsizing and auto-scaling recommended.")
if trend["cost_usd"].pct_change().max() > 0.4:
    st.warning("📉 Cost spikes detected. Enable budget alerts.")
if len(trend) >= 3:
    st.success("📊 Enough data available for cost forecasting.")

# ---------------------------
# Forecast
# ---------------------------
st.subheader("📊 Monthly Cost Forecast")

if len(trend) >= 2:
    growth = trend["cost_usd"].pct_change().mean()
    forecast = trend["cost_usd"].iloc[-1] * (1 + growth)
    st.metric("Next Month Forecast", f"${forecast:,.2f}")
else:
    st.info("Not enough data for forecast.")

# ---------------------------
# REPORT SUMMARY (NOT RAW DATA)
# ---------------------------
report_df = pd.DataFrame({
    "Metric": [
        "Total Cost",
        "Used Cost",
        "Idle Cost",
        "Idle Percentage",
        "FinOps Score"
    ],
    "Value": [
        f"${total_cost:,.2f}",
        f"${used_cost:,.2f}",
        f"${idle_cost:,.2f}",
        f"{idle_ratio*100:.1f}%",
        f"{finops_score}/5"
    ]
})

st.subheader("⬇️ Download Cost Reports")

c1, c2, c3 = st.columns(3)

# CSV
with c1:
    st.download_button(
        "✅ Download CSV Report",
        report_df.to_csv(index=False),
        "cloud_cost_summary.csv",
        "text/csv"
    )

# Excel
with c2:
    excel_buffer = BytesIO()
    report_df.to_excel(excel_buffer, index=False)
    st.download_button(
        "📊 Export Excel Cost Report",
        excel_buffer.getvalue(),
        "cloud_cost_summary.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# PDF
with c3:
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet

        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer)
        styles = getSampleStyleSheet()

        elements = [Paragraph("Cloud Cost Optimization Report", styles["Title"])]

        for _, row in report_df.iterrows():
            elements.append(Paragraph(f"{row['Metric']}: {row['Value']}", styles["Normal"]))

        doc.build(elements)

        st.download_button(
            "📄 Export PDF Cost Report",
            pdf_buffer.getvalue(),
            "cloud_cost_summary.pdf",
            "application/pdf"
        )
    except:
        st.info("PDF export available after installing reportlab")

st.caption("🚀 FinOps-Ready | Data-Driven | No Raw Data Exposure")
