import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

# -----------------------------
# Page config (NO zoom jump)
# -----------------------------
st.set_page_config(
    page_title="Cloud Cost Optimization Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("☁️ Cloud Cost Optimization Dashboard")

# -----------------------------
# Load data (ROBUST & SAFE)
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/cloud_cost.csv")

    # Handle mixed date formats safely
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
        format="mixed"
    )

    df = df.dropna(subset=["date"])

    # Ensure numeric cost
    df["cost_usd"] = pd.to_numeric(df["cost_usd"], errors="coerce").fillna(0)

    return df


df = load_data()

# -----------------------------
# Derived metrics (NO raw data shown)
# -----------------------------
total_cost = df["cost_usd"].sum()

# Assume 70% used, 30% idle (FinOps demo logic)
used_cost = total_cost * 0.7
idle_cost = total_cost * 0.3

# FinOps score (simple real logic)
if idle_cost / total_cost < 0.2:
    finops_score = 5
elif idle_cost / total_cost < 0.3:
    finops_score = 4
elif idle_cost / total_cost < 0.4:
    finops_score = 3
elif idle_cost / total_cost < 0.5:
    finops_score = 2
else:
    finops_score = 1

# -----------------------------
# KPI Cards
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Cost (USD)", f"${total_cost:,.2f}")
col2.metric("✅ Used Cost", f"${used_cost:,.2f}")
col3.metric("⚠️ Idle Cost", f"${idle_cost:,.2f}")
col4.metric("⭐ FinOps Score", f"{finops_score} / 5")

# -----------------------------
# Cost trend chart
# -----------------------------
trend = (
    df.groupby(pd.Grouper(key="date", freq="M"))["cost_usd"]
    .sum()
    .reset_index()
)

fig_trend = px.line(
    trend,
    x="date",
    y="cost_usd",
    title="📈 Monthly Cost Trend",
    markers=True
)

fig_trend.update_layout(
    dragmode=False,
    xaxis_fixedrange=True,
    yaxis_fixedrange=True
)

st.plotly_chart(fig_trend, use_container_width=True)

# -----------------------------
# Usage vs Idle chart
# -----------------------------
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

fig_usage.update_layout(
    dragmode=False
)

st.plotly_chart(fig_usage, use_container_width=True)

# -----------------------------
# AI-style insights (rule based)
# -----------------------------
st.subheader("🧠 AI-Based Cost Optimization Tips")

tips = []
if idle_cost / total_cost > 0.3:
    tips.append("🔻 High idle cost detected — consider rightsizing instances.")
if df["cost_usd"].max() > df["cost_usd"].mean() * 2:
    tips.append("📊 Cost spikes found — enable budget alerts.")
if len(trend) >= 3:
    tips.append("📈 Enough data for forecasting — plan reserved instances.")

if tips:
    for t in tips:
        st.success(t)
else:
    st.info("✅ Your cloud usage is well optimized.")

# -----------------------------
# Forecast (simple & stable)
# -----------------------------
st.subheader("📊 Monthly Cost Forecast")

if len(trend) >= 2:
    avg_growth = trend["cost_usd"].pct_change().mean()
    last_cost = trend["cost_usd"].iloc[-1]
    forecast_cost = last_cost * (1 + avg_growth)

    st.metric(
        "Next Month Forecast",
        f"${forecast_cost:,.2f}"
    )
else:
    st.info("Not enough data for forecasting.")

# -----------------------------
# DOWNLOAD SECTION (NO RAW TABLE)
# -----------------------------
st.subheader("⬇️ Download Reports")

col_a, col_b, col_c = st.columns(3)

# CSV
with col_a:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "✅ Download CSV Report",
        csv,
        "cloud_cost_report.csv",
        "text/csv"
    )

# Excel
with col_b:
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    st.download_button(
        "📊 Export Excel Cost Report",
        excel_buffer.getvalue(),
        "cloud_cost_report.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# PDF (safe – will NOT crash if missing lib)
with col_c:
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet

        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer)
        styles = getSampleStyleSheet()

        content = [
            Paragraph("Cloud Cost Optimization Report", styles["Title"]),
            Paragraph(f"Total Cost: ${total_cost:,.2f}", styles["Normal"]),
            Paragraph(f"Used Cost: ${used_cost:,.2f}", styles["Normal"]),
            Paragraph(f"Idle Cost: ${idle_cost:,.2f}", styles["Normal"]),
            Paragraph(f"FinOps Score: {finops_score}/5", styles["Normal"]),
        ]

        doc.build(content)

        st.download_button(
            "📄 Export PDF Cost Report",
            pdf_buffer.getvalue(),
            "cloud_cost_report.pdf",
            "application/pdf"
        )

    except Exception:
        st.warning("📄 PDF export requires reportlab (optional)")

# -----------------------------
# Footer
# -----------------------------
st.caption("🚀 FinOps-Ready | Portfolio-Grade Cloud Cost Dashboard")
