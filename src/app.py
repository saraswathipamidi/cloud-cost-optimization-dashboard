import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Cloud Cost Optimization Dashboard",
    layout="wide"
)

st.title("☁️ Cloud Cost Optimization Dashboard")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
   df = pd.read_csv("../data/cloud_costs.csv")
    df["billing_date"] = pd.to_datetime(df["billing_date"])
    return df

df = load_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔍 Filters")

providers = st.sidebar.multiselect(
    "Select Cloud Provider",
    options=df["cloud_provider"].unique(),
    default=df["cloud_provider"].unique()
)

filtered_df = df[df["cloud_provider"].isin(providers)]

# -----------------------------
# KPI METRICS
# -----------------------------
total_cost = filtered_df["cost_usd"].sum()
services_count = filtered_df["service"].nunique()
regions_count = filtered_df["region"].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Cost", f"${total_cost:,.2f}")
col2.metric("📦 Services", services_count)
col3.metric("🌍 Regions", regions_count)

st.divider()

# -----------------------------
# COST BY SERVICE
# -----------------------------
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

# -----------------------------
# COST TREND OVER TIME
# -----------------------------
st.subheader("📈 Cost Trend Over Time")

daily_cost = (
    filtered_df.groupby("billing_date")["cost_usd"]
    .sum()
    .reset_index()
)

fig_trend = px.line(
    daily_cost,
    x="billing_date",
    y="cost_usd",
    markers=True
)
st.plotly_chart(fig_trend, use_container_width=True)

# =====================================================
# ⭐ FINOPS SCORECARD (MAIN FEATURE)
# =====================================================
st.divider()
st.subheader("⭐ FinOps Scorecard")

# ---- FINOPS LOGIC ----

# 1️⃣ Cost Concentration
top_service_share = service_cost["cost_usd"].max() / total_cost

# 2️⃣ Regional Sprawl
region_penalty = max(0, regions_count - 3) * 5

# 3️⃣ Cost Growth
growth_rate = daily_cost["cost_usd"].pct_change().mean()

# 4️⃣ Waste Estimation (simple model)
waste_percentage = min(30, top_service_share * 100)

# ---- SCORING ----
score = 100

# Penalize concentration
if top_service_share > 0.4:
    score -= 15

# Penalize region sprawl
score -= region_penalty

# Penalize uncontrolled growth
if growth_rate and growth_rate > 0.05:
    score -= 10

# Penalize waste
score -= waste_percentage * 0.5

score = max(0, int(score))

# ---- GRADE ----
if score >= 85:
    grade = "A – Excellent"
    maturity = "Advanced"
elif score >= 70:
    grade = "B – Good"
    maturity = "Intermediate"
elif score >= 55:
    grade = "C – Needs Improvement"
    maturity = "Basic"
else:
    grade = "D – Poor"
    maturity = "Critical"

# ---- FINOPS METRICS DISPLAY ----
c1, c2, c3, c4 = st.columns(4)

c1.metric("🏆 FinOps Score", f"{score} / 100")
c2.metric("🎯 Grade", grade)
c3.metric("🧹 Waste Detected", f"{waste_percentage:.1f}%")
c4.metric("📊 Maturity Level", maturity)

# -----------------------------
# FINOPS RECOMMENDATIONS
# -----------------------------
st.subheader("🛠 FinOps Recommendations")

if top_service_share > 0.4:
    st.warning("⚠️ One service consumes most of your spend. Consider rightsizing or alternatives.")

if regions_count > 3:
    st.warning("🌍 Too many regions with low utilization. Consolidate workloads.")

if growth_rate and growth_rate > 0.05:
    st.warning("📈 Rapid cost growth detected. Enable budgets and alerts.")

if score >= 85:
    st.success("✅ Excellent FinOps practices! Keep optimizing.")
