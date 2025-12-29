import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="Cloud Cost Optimization Dashboard", layout="wide")

st.title("☁️ Cloud Cost Optimization Dashboard")

# -------------------------
# Load Data
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("../data/cloud_cost.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

df = load_data()

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("🔍 Filters")

provider = st.sidebar.multiselect(
    "Cloud Provider",
    options=df["cloud_provider"].unique(),
    default=df["cloud_provider"].unique()
)

service = st.sidebar.multiselect(
    "Service",
    options=df["service"].unique(),
    default=df["service"].unique()
)

filtered_df = df[
    (df["cloud_provider"].isin(provider)) &
    (df["service"].isin(service))
]

# -------------------------
# KPIs
# -------------------------
total_cost = filtered_df["cost"].sum()
avg_cost = filtered_df["cost"].mean()

st.metric("💰 Total Cost ($)", f"{total_cost:.2f}")
st.metric("📊 Average Cost ($)", f"{avg_cost:.4f}")

# -------------------------
# FinOps Scorecard
# -------------------------
st.subheader("⭐ FinOps Scorecard")

if total_cost < 50:
    score = 5
elif total_cost < 100:
    score = 4
elif total_cost < 200:
    score = 3
elif total_cost < 300:
    score = 2
else:
    score = 1

st.write(f"**Cost Efficiency Rating:** {'⭐' * score}")

# -------------------------
# Cost Over Time
# -------------------------
st.subheader("📈 Cost Trend Over Time")

trend = filtered_df.groupby(filtered_df["timestamp"].dt.date)["cost"].sum().reset_index()

fig = px.line(trend, x="timestamp", y="cost", title="Daily Cost Trend")
st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Cost by Service
# -------------------------
st.subheader("🧩 Cost by Service")

service_fig = px.bar(
    filtered_df.groupby("service")["cost"].sum().reset_index(),
    x="service",
    y="cost",
    title="Cost by Service"
)

st.plotly_chart(service_fig, use_container_width=True)
