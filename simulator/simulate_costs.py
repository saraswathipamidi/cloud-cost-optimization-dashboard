import pandas as pd
import random
import time
from datetime import datetime
import os

# -----------------------------
# CONFIG
# -----------------------------
DATA_PATH = "../data/cloud_cost.csv"
REFRESH_SECONDS = 5

providers = ["AWS", "Azure", "GCP"]
services = ["EC2", "S3", "RDS", "Lambda"]
regions = ["us-east-1", "us-west-2", "eu-west-1"]

# Base hourly costs (AWS-like)
BASE_COST = {
    "EC2": (0.02, 0.25),
    "S3": (0.01, 0.05),
    "RDS": (0.05, 0.30),
    "Lambda": (0.001, 0.02)
}

# -----------------------------
# INITIALIZE CSV IF NOT EXISTS
# -----------------------------
if not os.path.exists(DATA_PATH):
    df_init = pd.DataFrame(columns=[
        "date", "cloud_provider", "service", "region", "cost_usd"
    ])
    df_init.to_csv(DATA_PATH, index=False)

# -----------------------------
# SIMULATION LOOP
# -----------------------------
print("🚀 Starting cloud cost simulation...")

while True:
    record = {
        "date": datetime.now(),
        "cloud_provider": random.choice(providers),
        "service": random.choice(services),
        "region": random.choice(regions),
        "cost_usd": round(
            random.uniform(*BASE_COST[random.choice(services)]),
            4
        )
    }

    df = pd.DataFrame([record])
    df.to_csv(DATA_PATH, mode="a", header=False, index=False)

    print("Added:", record)

    time.sleep(REFRESH_SECONDS)
