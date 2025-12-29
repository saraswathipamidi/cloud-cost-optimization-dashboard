import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Cloud Cost Optimization Dashboard",
    layout="wide"
)

st.title("☁️ Cloud Cost Optimization Dashboard")
st.markdown("Analyze, optimize, and score your cloud costs using FinOps principles.")

# -------------------------------------------------
# Load Data (SAFE PATH FIXED)
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("../data/cloud_cost.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

df = load_data()

# -------------------------------------------------
# Sidebar Filters
# -------------------------------------------------
st.sidebar.header("🔍 Filters")

provider_filter = st.sidebar.multiselect(
    "Cloud Provider",
    options=df["cloud_provider"].unique(),
    default=df["cloud_provider"].unique()
)

service_filter = st.sidebar.multiselect(
    "Service",
    options=df["service"].unique(),
    default=df["service"].unique()
)

region_filter = st.sidebar.multiselect(
    "Region",
    options=df["region"].unique(),
    default=df["region"].unique()
)

filtered_df = df[
    (df["cloud_provider"].isin(provider_filter)) &
    (df["service"].isin(service_filter)) &
    (df["region"].isin(region_filter))
]

# -------------------------------------------------
# KPI SECTION
# -------------------------------------------------
st.subheader("📊 Key Metrics")

col1, col2, col3 = st.columns(3)

total_cost = filtered_df["cost"].sum()
avg_cost = filtered_df["cost"].mean()
max_cost = filtered_df["cost"].max()

col1.metric("💰 Total Cost ($)", f"{total_cost:.2f}")
col2.metric("📉 Average Cost ($)", f"{avg_cost:.4f}")
col3.metric("🔥 Highest Single Cost ($)", f"{max_cost:.4f}")

# -------------------------------------------------
# FinOps Scorecard (CORE FEATURE)
# -------------------------------------------------
st.subheader("⭐ FinOps Scorecard (Cost Efficiency Rating)")

if total_cost < 50:
    score = 5
    remark = "Excellent cost control"
elif total_cost < 100:
    score = 4
    remark = "Good optimization"
elif total_cost < 200:
    score = 3
    remark = "Moderate efficiency"
elif total_cost < 300:
    score = 2
    remark = "Needs optimization"
else:
    score = 1
    remark = "High cost – Immediate action needed"

st.markdown(f"""
### {'⭐' * score}
**Rating:** {score} / 5  
**Remark:** {remark}
""")

# -------------------------------------------------
# Cost Trend Over Time
# -------------------------------------------------
st.subheader("📈 Cost Trend Over Time")

daily_cost = (
    filtered_df
    .groupby(filtered_df["timestamp"].dt.date)["cost"]
    .sum()
    .reset_index()
)

trend_fig = px.line(
    daily_cost,
    x="timestamp",
    y="cost",
    title="Daily Cloud Cost Trend",
    markers=True
)

st.plotly_chart(trend_fig, use_container_width=True)

# -------------------------------------------------
# Cost by Cloud Provider
# -------------------------------------------------
st.subheader("☁️ Cost by Cloud Provider")

provider_cost = (
    filtered_df
    .groupby("cloud_provider")["cost"]
    .sum()
    .reset_index()
)

provider_fig = px.pie(
    provider_cost,
    names="cloud_provider",
    values="cost",
    title="Cost Distribution by Provider"
)

st.plotly_chart(provider_fig, use_container_width=True)

# -------------------------------------------------
# Cost by Service
# -------------------------------------------------
st.subheader("🧩 Cost by Service")

service_cost = (
    filtered_df
    .groupby("service")["cost"]
    .sum()
    .reset_index()
)

service_fig = px.bar(
    service_cost,
    x="service",
    y="cost",
    title="Service-wise Cost Breakdown"
)

st.plotly_chart(service_fig, use_container_width=True)

# -------------------------------------------------
# Cost by Region
# -------------------------------------------------
st.subheader("🌍 Cost by Region")

region_cost = (
    filtered_df
    .groupby("region")["cost"]
    .sum()
    .reset_index()
)

region_fig = px.bar(
    region_cost,
    x="region",
    y="cost",
    title="Region-wise Cost Distribution"
)

st.plotly_chart(region_fig, use_container_width=True)

# -------------------------------------------------
# Raw Data Viewer
# -------------------------------------------------
st.subheader("📄 Raw Cost Data")

st.dataframe(filtered_df, use_container_width=True)
