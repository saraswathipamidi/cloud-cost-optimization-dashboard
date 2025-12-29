import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Cloud Cost Optimization Dashboard",
    layout="wide"
)

st.title("☁️ Cloud Cost Optimization Dashboard")

# -----------------------------
# LOAD DATA (STREAMLIT CLOUD SAFE)
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("../data/cloud_costs.csv")

    # Standardize column names
    df.columns = df.columns.str.lower().str.strip()

    # Rename columns if needed
    rename_map = {
        "date": "billing_date",
        "cost": "cost_usd",
        "provider": "cloud_provider"
    }
    df.rename(columns=rename_map, inplace=True)

    # Convert datatypes
    df["billing_date"] = pd.to_datetime(df["billing_date"])
    df["cost_usd"] = pd.to_numeric(df["cost_usd"], errors="coerce")

    return df

df = load_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔍 Filters")

providers = ["All"] + sorted(df["cloud_provider"].dropna().unique().tolist())
selected_provider = st.sidebar.selectbox("Cloud Provider", providers)

filtered_df = df.copy()
if selected_provider != "All":
    filtered_df = filtered_df[
        filtered_df["cloud_provider"] == selected_provider
    ]

# -----------------------------
# METRICS
# -----------------------------
total_cost = filtered_df["cost_usd"].sum()
total_records = len(filtered_df)

col1, col2 = st.columns(2)
col1.metric("💰 Total Cost", f"${total_cost:,.2f}")
col2.metric("📄 Records", total_records)

# -----------------------------
# COST BY PROVIDER
# -----------------------------
st.subheader("📊 Cost by Cloud Provider")

provider_cost = (
    filtered_df
    .groupby("cloud_provider", as_index=False)["cost_usd"]
    .sum()
)

fig_provider = px.bar(
    provider_cost,
    x="cloud_provider",
    y="cost_usd",
    text_auto=".2s",
    title="Total Cost by Provider"
)

st.plotly_chart(fig_provider, use_container_width=True)

# -----------------------------
# COST BY SERVICE
# -----------------------------
st.subheader("🧩 Cost by Service")

service_cost = (
    filtered_df
    .groupby("service", as_index=False)["cost_usd"]
    .sum()
    .sort_values("cost_usd", ascending=False)
)

fig_service = px.bar(
    service_cost,
    x="service",
    y="cost_usd",
    color="service",
    text_auto=".2s",
    title="Total Cost by Service"
)

st.plotly_chart(fig_service, use_container_width=True)

# -----------------------------
# COST BY REGION
# -----------------------------
st.subheader("🌍 Cost by Region")

region_cost = (
    filtered_df
    .groupby("region", as_index=False)["cost_usd"]
    .sum()
    .sort_values("cost_usd", ascending=False)
)

fig_region = px.bar(
    region_cost,
    x="region",
    y="cost_usd",
    color="region",
    text_auto=".2s",
    title="Total Cost by Region"
)

st.plotly_chart(fig_region, use_container_width=True)

# -----------------------------
# COST TREND OVER TIME
# -----------------------------
st.subheader("📈 Cost Trend Over Time")

trend_df = (
    filtered_df
    .groupby("billing_date", as_index=False)["cost_usd"]
    .sum()
)

fig_trend = px.line(
    trend_df,
    x="billing_date",
    y="cost_usd",
    markers=True,
    title="Daily Cost Trend"
)

st.plotly_chart(fig_trend, use_container_width=True)

# -----------------------------
# FINOPS SCORECARD ⭐⭐⭐⭐⭐
# -----------------------------
st.subheader("⭐ FinOps Cost Efficiency Scorecard")

avg_daily_cost = trend_df["cost_usd"].mean()

if avg_daily_cost < 50:
    score = 5
    rating = "Excellent 🟢"
elif avg_daily_cost < 100:
    score = 4
    rating = "Good 🟡"
elif avg_daily_cost < 200:
    score = 3
    rating = "Average 🟠"
else:
    score = 2
    rating = "Needs Optimization 🔴"

st.metric("FinOps Score (out of 5)", f"{score} ⭐")
st.write(f"**Cost Efficiency Rating:** {rating}")
st.write(f"**Average Daily Cost:** ${avg_daily_cost:,.2f}")

# -----------------------------
# RAW DATA
# -----------------------------
with st.expander("📄 View Raw Data"):
    st.dataframe(filtered_df)
