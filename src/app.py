import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Cloud Cost Optimization Dashboard",
    page_icon="☁️",
    layout="wide"
)

st.title("☁️ Cloud Cost Optimization Dashboard")

# ----------------------------
# LOAD DATA (CLOUD SAFE)
# ----------------------------
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "data", "cloud_costs.csv")
    df = pd.read_csv(DATA_PATH)
    df["billing_date"] = pd.to_datetime(df["billing_date"])
    return df

df = load_data()

# ----------------------------
# SIDEBAR FILTERS
# ----------------------------
st.sidebar.header("🔎 Filters")

providers = st.sidebar.multiselect(
    "Select Cloud Provider",
    options=df["cloud_provider"].unique(),
    default=df["cloud_provider"].unique()
)

filtered_df = df[df["cloud_provider"].isin(providers)]

# ----------------------------
# KPI METRICS
# ----------------------------
total_cost = filtered_df["cost_usd"].sum()
services_count = filtered_df["service"].nunique()
regions_count = filtered_df["region"].nunique()

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Cost", f"${total_cost:,.2f}")
col2.metric("📦 Services", services_count)
col3.metric("🌍 Regions", regions_count)

st.divider()

# ----------------------------
# COST BY SERVICE
# ----------------------------
st.subheader("📊 Cost by Service")

service_cost = (
    filtered_df.groupby("service")["cost_usd"]
    .sum()
    .reset_index()
)

fig_service = px.bar(
    service_cost,
    x="service",
    y="cost_usd",
    text_auto=".2s"
)
st.plotly_chart(fig_service, use_container_width=True)

# ----------------------------
# COST BY REGION
# ----------------------------
st.subheader("🌍 Cost by Region")

region_cost = (
    filtered_df.groupby("region")["cost_usd"]
    .sum()
    .reset_index()
)

fig_region = px.pie(
    region_cost,
    names="region",
    values="cost_usd",
    hole=0.4
)
st.plotly_chart(fig_region, use_container_width=True)

# ----------------------------
# COST TREND OVER TIME
# ----------------------------
st.subheader("📈 Cost Trend Over Time")

trend_df = (
    filtered_df.groupby("billing_date")["cost_usd"]
    .sum()
    .reset_index()
)

fig_trend = px.line(
    trend_df,
    x="billing_date",
    y="cost_usd",
    markers=True
)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ----------------------------
# FINOPS SCORECARD ⭐⭐⭐⭐⭐
# ----------------------------
st.subheader("⭐ FinOps Cost Efficiency Scorecard")

avg_daily_cost = trend_df["cost_usd"].mean()
max_service_cost = service_cost["cost_usd"].max()
cost_variance = trend_df["cost_usd"].std()

score = 100

if avg_daily_cost > 500:
    score -= 20
if max_service_cost > total_cost * 0.6:
    score -= 20
if cost_variance > avg_daily_cost * 0.5:
    score -= 20

if score >= 80:
    rating = "⭐⭐⭐⭐⭐ Excellent"
elif score >= 60:
    rating = "⭐⭐⭐⭐ Good"
elif score >= 40:
    rating = "⭐⭐⭐ Average"
else:
    rating = "⭐⭐ Needs Optimization"

col1, col2 = st.columns(2)
col1.metric("FinOps Score", f"{score}/100")
col2.metric("Efficiency Rating", rating)

st.info(
    """
**How FinOps Score is calculated**
- Average daily spend
- Cost concentration in one service
- Daily cost volatility

Higher score = better cost governance
"""
)

# ----------------------------
# FOOTER
# ----------------------------
st.caption("🚀 Built with Streamlit | Cloud FinOps Dashboard")
