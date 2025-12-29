import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Cloud Cost Optimization Dashboard", layout="wide")

st.title("☁️ Cloud Cost Optimization Dashboard")

# -------------------------------
# Load Data (SAFE & CORRECT PATH)
# -------------------------------
@st.cache_data
def load_data():
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, "..", "data", "cloud_cost.csv")
    df = pd.read_csv(data_path)

    # Ensure date column
    if "billing_date" in df.columns:
        df["billing_date"] = pd.to_datetime(df["billing_date"])

    return df


df = load_data()

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("Filters")

cloud = st.sidebar.selectbox(
    "Select Cloud Provider",
    options=["All"] + sorted(df["cloud_provider"].unique().tolist())
)

if cloud != "All":
    df = df[df["cloud_provider"] == cloud]

# -------------------------------
# KPI Metrics
# -------------------------------
st.subheader("📊 Key Metrics")

total_cost = df["cost_usd"].sum()
avg_cost = df["cost_usd"].mean()
max_cost = df["cost_usd"].max()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Cost (USD)", f"${total_cost:,.2f}")
col2.metric("📈 Average Cost", f"${avg_cost:,.2f}")
col3.metric("🚨 Highest Cost", f"${max_cost:,.2f}")

# -------------------------------
# FinOps Scorecard ⭐
# -------------------------------
st.subheader("⭐ FinOps Scorecard")

score = 5
if avg_cost > 300:
    score = 2
elif avg_cost > 200:
    score = 3
elif avg_cost > 100:
    score = 4

st.markdown(f"### Cost Efficiency Rating: {'⭐' * score}")

# -------------------------------
# Charts
# -------------------------------
st.subheader("📉 Cost Trend Over Time")

if "billing_date" in df.columns:
    trend = df.groupby("billing_date")["cost_usd"].sum()
    st.line_chart(trend)

st.subheader("📦 Cost by Service")
service_cost = df.groupby("service")["cost_usd"].sum()
st.bar_chart(service_cost)

st.subheader("📍 Cost by Region")
region_cost = df.groupby("region")["cost_usd"].sum()
st.bar_chart(region_cost)

# -------------------------------
# Raw Data
# -------------------------------
st.subheader("🧾 Raw Cost Data")
st.dataframe(df)
