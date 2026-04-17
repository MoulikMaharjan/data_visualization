import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import glob

st.title("📊 Orders Analytics Dashboard")

# Load CSV files
files = glob.glob('*.csv')
files = [f for f in files if 'merged1.csv' not in f]

if len(files) == 0:
    st.error("No CSV files found")
else:
    df = pd.concat(map(pd.read_csv, files), ignore_index=True)

    # Process data
    df['shipDate'] = pd.to_datetime(df['shipDate'])
    df['date'] = df['shipDate'].dt.date
    df['month'] = df['shipDate'].dt.to_period('M')

    # Metrics
    order_per_day = df.groupby('date').size()
    order_per_month = df.groupby('month').size()

    # Growth
    monthly_growth = order_per_month.pct_change().fillna(0) * 100

    # =========================
    # KPI Section
    # =========================
    st.subheader("📌 Key Metrics")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", len(df))
    col2.metric("Max Orders/Day", order_per_day.max())
    col3.metric("Avg Orders/Day", int(order_per_day.mean()))

    # =========================
    # Orders per Day
    # =========================
    st.subheader("📈 Orders Per Day")
    st.line_chart(order_per_day)

    # =========================
    # Orders per Month
    # =========================
    st.subheader("📊 Orders Per Month")
    st.bar_chart(order_per_month)

    # =========================
    # Growth Rate
    # =========================
    st.subheader("🚀 Monthly Growth (%)")
    st.line_chart(monthly_growth)

    # =========================
    # Top 10 Days
    # =========================
    st.subheader("🔥 Top 10 Days")
    top10 = order_per_day.sort_values(ascending=False).head(10)
    st.bar_chart(top10)