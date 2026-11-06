"""Streamlit dashboard for SalesLens. Run: streamlit run app.py"""
import json
from pathlib import Path
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from src.config import ROOT_DIR, OUTPUT_DIR, CHART_DIR, PROCESSED_DIR
from src.analysis import load_source_data, prepare_data, make_summary, build_rfm

st.set_page_config(page_title="SalesLens | Retail Analytics", page_icon="📊", layout="wide")
st.title("📊 SalesLens")
st.caption("Retail sales analytics using Python, SQL and data visualisation")

@st.cache_data
def get_data():
    raw, source = load_source_data(ROOT_DIR)
    sales, quality = prepare_data(raw)
    rfm = build_rfm(sales)
    return sales, quality, rfm, source

try:
    sales, quality, rfm, source = get_data()
except Exception as exc:
    st.error(f"Could not load dataset: {exc}")
    st.info("See data/README.md for instructions. The included synthetic demo sample should load by default.")
    st.stop()

st.info(f"Data source: {source}")
if "SYNTHETIC" in source:
    st.warning("DEMO DATA: The included sample is synthetic and is only for testing the project. Download the official UCI dataset for real analysis.")
summary=make_summary(sales)
cols=st.columns(4)
cols[0].metric("Revenue", f"£{summary['total_revenue_gbp']:,.2f}")
cols[1].metric("Invoices", f"{summary['invoices']:,}")
cols[2].metric("Products", f"{summary['products']:,}")
cols[3].metric("Customers with ID", f"{summary['customers_with_id']:,}")

st.subheader("Sales overview")
monthly=sales.groupby("InvoiceMonth",as_index=False)["Revenue"].sum().sort_values("InvoiceMonth")
fig,ax=plt.subplots(figsize=(11,4)); ax.plot(monthly["InvoiceMonth"],monthly["Revenue"],marker="o"); ax.set_xlabel("Month"); ax.set_ylabel("Revenue (£)"); ax.grid(alpha=.25); plt.xticks(rotation=45); fig.tight_layout(); st.pyplot(fig); plt.close(fig)
left,right=st.columns(2)
with left:
    st.subheader("Top products by revenue")
    top=sales.groupby("Description")["Revenue"].sum().nlargest(10).sort_values()
    st.bar_chart(top)
with right:
    st.subheader("Revenue by country")
    country=sales.groupby("Country")["Revenue"].sum().nlargest(10).sort_values()
    st.bar_chart(country)

st.subheader("Customer segments (rule-based RFM)")
if not rfm.empty:
    st.bar_chart(rfm["Segment"].value_counts())
else:
    st.write("No identified customers in this dataset.")

with st.expander("Data quality and methodology"):
    st.write("Sales KPIs use positive-quantity, positive-price records whose invoice number is not marked as a cancellation. Missing customer IDs are retained in sales totals but excluded from customer-level RFM analysis.")
    st.json(quality)
    st.write("Average order value is calculated as total revenue divided by unique invoices. Currency is GBP (£), as specified by the source dataset.")

st.subheader("Explore cleaned transactions")
st.dataframe(sales.head(100),use_container_width=True)
st.download_button("Download cleaned sales CSV",sales.to_csv(index=False).encode("utf-8"),file_name="saleslens_cleaned_sales.csv",mime="text/csv")
