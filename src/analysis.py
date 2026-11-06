"""Data preparation and analysis for SalesLens.

The default input is a small synthetic sample included for an immediate demo.
For full analysis, place UCI's Online Retail.xlsx in data/raw/.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np

REQUIRED_COLUMNS = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"]


def load_source_data(root: Path) -> tuple[pd.DataFrame, str]:
    """Load the official workbook when present; otherwise load the labelled sample."""
    candidates = [root / "data/raw/Online Retail.xlsx", root / "data/raw/online_retail.xlsx"]
    for path in candidates:
        if path.exists():
            return pd.read_excel(path), f"UCI full dataset: {path.name}"
    csv_path = root / "data/raw/online_retail.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path), f"User-provided raw CSV: {csv_path.name}"
    sample_path = root / "data/sample/online_retail_sample.csv"
    if sample_path.exists():
        return pd.read_csv(sample_path), "SYNTHETIC DEMO SAMPLE (not original UCI observations)"
    raise FileNotFoundError("No dataset found. See data/README.md for setup instructions.")


def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise common UCI column names and validate required fields."""
    aliases = {c.lower().replace(" ", ""): c for c in REQUIRED_COLUMNS}
    rename = {}
    for col in df.columns:
        key = str(col).lower().replace(" ", "")
        if key in aliases:
            rename[col] = aliases[key]
    out = df.rename(columns=rename).copy()
    missing = [c for c in REQUIRED_COLUMNS if c not in out.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")
    return out[REQUIRED_COLUMNS]


def prepare_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean raw data and return valid completed sales plus quality metrics."""
    data = standardise_columns(df)
    original_rows = len(data)
    data["InvoiceNo"] = data["InvoiceNo"].astype(str).str.strip()
    data["StockCode"] = data["StockCode"].astype(str).str.strip()
    data["Description"] = data["Description"].astype("string").str.strip()
    data["Country"] = data["Country"].astype("string").str.strip()
    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"], errors="coerce")
    data["Quantity"] = pd.to_numeric(data["Quantity"], errors="coerce")
    data["UnitPrice"] = pd.to_numeric(data["UnitPrice"], errors="coerce")
    data["CustomerID"] = pd.to_numeric(data["CustomerID"], errors="coerce")
    duplicate_rows = int(data.duplicated().sum())
    data = data.drop_duplicates().copy()
    data["is_cancellation"] = data["InvoiceNo"].str.upper().str.startswith("C")
    cancellation_rows = int(data["is_cancellation"].sum())
    missing_customer_rows = int(data["CustomerID"].isna().sum())
    invalid_date_rows = int(data["InvoiceDate"].isna().sum())
    invalid_price_rows = int((data["UnitPrice"].isna() | (data["UnitPrice"] <= 0)).sum())
    invalid_quantity_rows = int((data["Quantity"].isna() | (data["Quantity"] <= 0)).sum())
    # For sales KPIs, use positive-quantity, positive-price, non-cancellation lines.
    valid = data[
        (~data["is_cancellation"])
        & data["InvoiceDate"].notna()
        & data["Quantity"].notna() & (data["Quantity"] > 0)
        & data["UnitPrice"].notna() & (data["UnitPrice"] > 0)
        & data["InvoiceNo"].notna()
        & data["StockCode"].notna()
    ].copy()
    valid["Revenue"] = (valid["Quantity"] * valid["UnitPrice"]).round(2)
    valid["InvoiceDate"] = pd.to_datetime(valid["InvoiceDate"])
    valid["CustomerID"] = valid["CustomerID"].astype("Int64")
    valid["InvoiceMonth"] = valid["InvoiceDate"].dt.to_period("M").astype(str)
    valid["InvoiceHour"] = valid["InvoiceDate"].dt.hour
    metrics = {
        "original_rows": original_rows,
        "duplicate_rows_removed": duplicate_rows,
        "cancellation_rows_excluded": cancellation_rows,
        "missing_customer_rows_in_source": missing_customer_rows,
        "invalid_date_rows_in_source": invalid_date_rows,
        "invalid_price_rows_in_source": invalid_price_rows,
        "invalid_quantity_rows_in_source": invalid_quantity_rows,
        "clean_sales_rows": len(valid),
        "unique_invoices": int(valid["InvoiceNo"].nunique()),
        "unique_products": int(valid["StockCode"].nunique()),
        "unique_customers_with_id": int(valid["CustomerID"].nunique()),
    }
    return valid, metrics


def build_rfm(sales: pd.DataFrame) -> pd.DataFrame:
    """Create simple, explainable RFM features and rule-based customer groups."""
    customers = sales.dropna(subset=["CustomerID"]).copy()
    if customers.empty:
        return pd.DataFrame(columns=["CustomerID", "RecencyDays", "Frequency", "Monetary", "Segment"])
    reference_date = customers["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)
    rfm = customers.groupby("CustomerID").agg(
        LastPurchase=("InvoiceDate", "max"),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum"),
    ).reset_index()
    rfm["RecencyDays"] = (reference_date - rfm["LastPurchase"].dt.normalize()).dt.days
    # Rule-based groups are deliberately transparent for a beginner project.
    r_med, f_med, m_med = rfm["RecencyDays"].median(), rfm["Frequency"].median(), rfm["Monetary"].median()
    def segment(row):
        if row.RecencyDays <= r_med and row.Frequency >= f_med and row.Monetary >= m_med:
            return "Champions"
        if row.Frequency >= f_med and row.RecencyDays <= r_med:
            return "Loyal Customers"
        if row.RecencyDays >= r_med and row.Frequency >= f_med:
            return "At Risk"
        if row.RecencyDays <= r_med:
            return "Recent Customers"
        return "Regular Customers"
    rfm["Segment"] = rfm.apply(segment, axis=1)
    return rfm[["CustomerID", "RecencyDays", "Frequency", "Monetary", "Segment"]].sort_values("Monetary", ascending=False)


def make_summary(sales: pd.DataFrame) -> dict:
    """Return portfolio-level KPIs; monetary values are in GBP (£)."""
    return {
        "total_revenue_gbp": round(float(sales["Revenue"].sum()), 2),
        "total_units_sold": int(sales["Quantity"].sum()),
        "invoices": int(sales["InvoiceNo"].nunique()),
        "products": int(sales["StockCode"].nunique()),
        "customers_with_id": int(sales["CustomerID"].nunique()),
        "countries": int(sales["Country"].nunique()),
        "average_order_value_gbp": round(float(sales.groupby("InvoiceNo")["Revenue"].sum().mean()), 2),
    }


def make_charts(sales: pd.DataFrame, rfm: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Create core portfolio charts and return saved file paths."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    output_dir.mkdir(parents=True, exist_ok=True)
    saved=[]
    monthly=sales.groupby("InvoiceMonth")["Revenue"].sum().sort_index()
    fig,ax=plt.subplots(figsize=(10,5)); monthly.plot(ax=ax,marker="o")
    ax.set(title="Monthly Revenue",xlabel="Month",ylabel="Revenue (£)"); ax.grid(alpha=.25); fig.tight_layout()
    p=output_dir/"monthly_revenue.png"; fig.savefig(p,dpi=150); plt.close(fig); saved.append(p)
    top=sales.groupby("Description")["Revenue"].sum().nlargest(10).sort_values()
    fig,ax=plt.subplots(figsize=(10,6)); top.plot(kind="barh",ax=ax)
    ax.set(title="Top 10 Products by Revenue",xlabel="Revenue (£)",ylabel="Product"); fig.tight_layout()
    p=output_dir/"top_products.png"; fig.savefig(p,dpi=150); plt.close(fig); saved.append(p)
    country=sales.groupby("Country")["Revenue"].sum().nlargest(10).sort_values()
    fig,ax=plt.subplots(figsize=(10,6)); country.plot(kind="barh",ax=ax)
    ax.set(title="Top 10 Countries by Revenue",xlabel="Revenue (£)",ylabel="Country"); fig.tight_layout()
    p=output_dir/"country_revenue.png"; fig.savefig(p,dpi=150); plt.close(fig); saved.append(p)
    hourly=sales.groupby("InvoiceHour")["InvoiceNo"].nunique()
    fig,ax=plt.subplots(figsize=(10,5)); hourly.plot(kind="bar",ax=ax)
    ax.set(title="Orders by Hour of Day",xlabel="Hour (24-hour clock)",ylabel="Unique invoices"); fig.tight_layout()
    p=output_dir/"orders_by_hour.png"; fig.savefig(p,dpi=150); plt.close(fig); saved.append(p)
    if not rfm.empty:
        counts=rfm["Segment"].value_counts()
        fig,ax=plt.subplots(figsize=(8,5)); counts.plot(kind="bar",ax=ax)
        ax.set(title="Customer Segments (Rule-Based RFM)",xlabel="Segment",ylabel="Customers"); ax.tick_params(axis="x",rotation=25); fig.tight_layout()
        p=output_dir/"customer_segments.png"; fig.savefig(p,dpi=150); plt.close(fig); saved.append(p)
    return saved
