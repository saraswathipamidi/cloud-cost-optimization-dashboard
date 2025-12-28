import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest
from fpdf import FPDF
import io
from datetime import datetime, timedelta

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Cloud Cost Optimization Dashboard", layout="wide")
st.title("☁️ Cloud Cost Optimization Dashboard")

# =============================
# SIMULATED AWS-LIKE DATA
# =============================
np.random.seed(42)

dates = pd.date_range(
    start=datetime.now() - timedelta(days=6),
    end=datetime.now(),
    freq="D"
)

cloud_providers = ["AWS", "Azure", "GCP"]
services = ["EC2", "S3", "RDS", "Lambda", "CloudWatch"]
regions = ["us-east-1", "us-west-2", "ap-south-1"]

data = []
for d in dates:
    for _ in range(10):
        data.append([
            d,
            np.random.choice(cloud_providers),
            np.random.choice(services),
            np.random.choice(regions),
            round(np.random.uniform(10, 200), 2)
        ])

df = pd.DataFrame(
    data,
    columns=["billing_date", "cloud_provider", "service", "region", "cost_usd"]
)

# =============================
# SIDEBAR FILTERS
# =============================
st.sidebar.header("🔍 Filters")

providers = st.sidebar.multiselect(
    "Select Cloud Provider",
    df["cloud_provider"].unique(),
    default=df["cloud_provider"].unique()
)

filtered_df = df[df["cloud_provider"].isin(providers)]

# =============================
# METRICS
# =============================
col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Cost", f"${filtered_df['cost_usd'].sum():,.2f}")
col2.metric("📦 Services", filtered_df["service"].nunique())
col3.metric("🌍 Regions", filtered_df["region"].nunique())

st.divider()

# =============================
# COST BY SERVICE
# =============================
st.subheader("📊 Cost by Service")

service_cost = filtered_df.groupby("service")["cost_usd"].sum().reset_index()
st.plotly_chart(
    px.bar(service_cost, x="service", y="cost_usd", text_auto=".2s"),
    use_container_width=True
)

# =============================
# COST BY REGION
# =============================
st.subheader("🌍 Cost by Region")

region_cost = filtered_df.groupby("region")["cost_usd"].sum().reset_index()
st.plotly_chart(
    px.bar(region_cost, x="region", y="cost_usd", text_auto=".2s"),
    use_container_width=True
)

# =============================
# COST TREND
# =============================
st.subheader("📈 Cost Trend Over Time")

trend_df = filtered_df.groupby("billing_date")["cost_usd"].sum().reset_index()
st.plotly_chart(
    px.line(trend_df, x="billing_date", y="cost_usd", markers=True),
    use_container_width=True
)

# =============================
# ANOMALY DETECTION (ML)
# =============================
st.subheader("🚨 Cost Anomaly Detection")

model = IsolationForest(contamination=0.15, random_state=42)
trend_df["anomaly"] = model.fit_predict(trend_df[["cost_usd"]])

anomalies = trend_df[trend_df["anomaly"] == -1]

if anomalies.empty:
    st.success("✅ No anomalies detected")
else:
    st.warning("⚠️ Anomalies detected")
    st.dataframe(anomalies)

# =============================
# OPTIMIZATION RECOMMENDATIONS
# =============================
st.subheader("💡 Optimization Recommendations")

st.markdown("### 🔧 High Cost Services")
st.dataframe(service_cost.sort_values("cost_usd", ascending=False).head(3))

st.markdown("### 🌍 High Cost Regions")
st.dataframe(region_cost.sort_values("cost_usd", ascending=False).head(3))

# =============================
# SAVINGS ESTIMATION
# =============================
st.subheader("💸 Estimated Monthly Savings")

service_savings = service_cost["cost_usd"].nlargest(3).sum() * 0.2
region_savings = region_cost["cost_usd"].nlargest(3).sum() * 0.15

c1, c2, c3 = st.columns(3)
c1.metric("Service Savings", f"${service_savings:,.2f}")
c2.metric("Region Savings", f"${region_savings:,.2f}")
c3.metric("Total Savings", f"${service_savings + region_savings:,.2f}")

st.divider()

# =============================
# PHASE 2 – EXPORT REPORTS
# =============================
st.subheader("📤 Export Cost Reports")

# -------- EXCEL EXPORT --------
excel_buffer = io.BytesIO()
filtered_df.to_excel(excel_buffer, index=False)
excel_buffer.seek(0)

st.download_button(
    "⬇️ Download Excel Report",
    excel_buffer,
    file_name="cloud_cost_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# -------- PDF EXPORT (FIXED) --------
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=10)

pdf.cell(0, 10, "Cloud Cost Optimization Report", ln=True)

for _, row in filtered_df.head(40).iterrows():
    pdf.cell(
        0,
        8,
        f"{row['billing_date']} | {row['cloud_provider']} | {row['service']} | "
        f"{row['region']} | ${row['cost_usd']}",
        ln=True
    )

pdf_bytes = pdf.output(dest="S").encode("latin-1")

st.download_button(
    "⬇️ Download PDF Report",
    pdf_bytes,
    file_name="cloud_cost_report.pdf",
    mime="application/pdf"
)
