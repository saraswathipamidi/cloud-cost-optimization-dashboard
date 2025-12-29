import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="Cloud Cost Optimization Dashboard",
    layout="wide"
)

st.title("☁️ Cloud Cost Optimization Dashboard")

# -------------------------
# Load data
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/cloud_costs.csv")
    df["billing_date"] = pd.to_datetime(df["billing_date"])
    return df

df = load_data()

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("🔍 Filters")

providers = st.sidebar.multiselect(
    "Select Cloud Provider",
    options=df["cloud_provider"].unique(),
    default=df["cloud_provider"].unique()
)

filtered_df = df[df["cloud_provider"].isin(providers)]

# -------------------------
# KPI Metrics
# -------------------------
total_cost = filtered_df["cost_usd"].sum()
services_count = filtered_df["service"].nunique()
regions_count = filtered_df["region"].nunique()

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Cost (USD)", f"${total_cost:,.2f}")
col2.metric("📦 Services", services_count)
col3.metric("🌍 Regions", regions_count)

st.divider()

# -------------------------
# FinOps Scorecard
# -------------------------
st.subheader("⭐ FinOps Cost Efficiency Scorecard")

daily_cost = (
    filtered_df.groupby("billing_date", as_index=False)["cost_usd"].sum()
)

avg_daily_cost = daily_cost["cost_usd"].mean()

# Scoring Logic (simple but effective)
score = 100

if avg_daily_cost > 500:
    score -= 25

if services_count > 6:
    score -= 20

if regions_count > 4:
    score -= 15

if daily_cost["cost_usd"].iloc[-1] > daily_cost["cost_usd"].iloc[0]:
    score -= 20

score = max(score, 0)

# Rating
if score >= 80:
    rating = "⭐⭐⭐⭐⭐ Excellent"
elif score >= 60:
    rating = "⭐⭐⭐⭐ Good"
elif score >= 40:
    rating = "⭐⭐⭐ Average"
else:
    rating = "⭐⭐ Needs Optimization"

colA, colB = st.columns(2)

colA.metric("FinOps Score", f"{score} / 100")
colB.metric("Efficiency Rating", rating)

st.info(
    "This FinOps score evaluates cloud cost efficiency based on spend trend, "
    "number of services, regions, and average daily cost."
)

st.divider()

# -------------------------
# Cost by Service
# -------------------------
st.subheader("📊 Cost by Service")

service_cost = (
    filtered_df.groupby("service", as_index=False)["cost_usd"].sum()
)

fig_service = px.bar(
    service_cost,
    x="service",
    y="cost_usd",
    text_auto=".2s",
    title="Cost Distribution by Service"
)

st.plotly_chart(fig_service, use_container_width=True)

# -------------------------
# Cost Over Time
# -------------------------
st.subheader("📈 Cost Over Time")

time_cost = (
    filtered_df.groupby("billing_date", as_index=False)["cost_usd"].sum()
)

fig_time = px.line(
    time_cost,
    x="billing_date",
    y="cost_usd",
    markers=True,
    title="Cloud Cost Trend Over Time"
)

st.plotly_chart(fig_time, use_container_width=True)
