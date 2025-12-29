import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import io

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Cloud Cost Optimization Dashboard",
    layout="wide"
)

st.title("☁️ Cloud Cost Optimization Dashboard")

# -----------------------------
# Load Data (SAFE PATH)
# -----------------------------
@st.cache_data
def load_data():
    data_path = Path(__file__).parent.parent / "data" / "cloud_cost.csv"
    df = pd.read_csv(data_path)

    df.columns = ["date", "cloud_provider", "service", "region", "cost_usd"]
    df["date"] = pd.to_datetime(df["date"])
    df["cost_usd"] = df["cost_usd"].astype(float)

    return df

df = load_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔍 Filters")

provider_filter = st.sidebar.selectbox(
    "Select Cloud Provider",
    ["All"] + sorted(df["cloud_provider"].unique())
)

if provider_filter != "All":
    df = df[df["cloud_provider"] == provider_filter]

# -----------------------------
# Key Metrics
# -----------------------------
total_cost = df["cost_usd"].sum()
avg_cost = df["cost_usd"].mean()
max_cost = df["cost_usd"].max()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Cost (USD)", f"${total_cost:,.2f}")
col2.metric("📊 Average Cost", f"${avg_cost:,.2f}")
col3.metric("🔥 Highest Cost", f"${max_cost:,.2f}")

# -----------------------------
# FinOps Scorecard
# -----------------------------
st.subheader("⭐ FinOps Scorecard")

if total_cost < 500:
    score = 5
elif total_cost < 1000:
    score = 4
elif total_cost < 1500:
    score = 3
else:
    score = 2

st.write("Cost Efficiency Rating:", "⭐" * score)

# -----------------------------
# Cost Trend Over Time
# -----------------------------
st.subheader("📈 Cost Trend Over Time")

trend_df = df.groupby("date", as_index=False)["cost_usd"].sum()

fig_trend = px.line(
    trend_df,
    x="date",
    y="cost_usd",
    markers=True
)
st.plotly_chart(fig_trend, use_container_width=True)

# -----------------------------
# Cost by Service
# -----------------------------
st.subheader("📦 Cost by Service")

service_df = df.groupby("service", as_index=False)["cost_usd"].sum()

fig_service = px.bar(
    service_df,
    x="service",
    y="cost_usd"
)
st.plotly_chart(fig_service, use_container_width=True)

# -----------------------------
# Cost by Region
# -----------------------------
st.subheader("📍 Cost by Region")

region_df = df.groupby("region", as_index=False)["cost_usd"].sum()

fig_region = px.bar(
    region_df,
    x="region",
    y="cost_usd"
)
st.plotly_chart(fig_region, use_container_width=True)

# -----------------------------
# Raw Data Table
# -----------------------------
st.subheader("📋 Raw Cost Data")
st.dataframe(df, use_container_width=True)

# -----------------------------
# Download Reports
# -----------------------------
st.subheader("⬇️ Export Cost Report")

# CSV Download
st.download_button(
    label="⬇️ Download CSV",
    data=df.to_csv(index=False),
    file_name="cloud_cost_report.csv",
    mime="text/csv"
)

# Excel Download
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Cloud Costs")

st.download_button(
    label="📥 Download Excel",
    data=excel_buffer.getvalue(),
    file_name="cloud_cost_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
