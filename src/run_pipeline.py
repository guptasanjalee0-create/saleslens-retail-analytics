from pathlib import Path
import json
import pandas as pd
from .config import ROOT_DIR, PROCESSED_DIR, OUTPUT_DIR, CHART_DIR, DB_PATH
from .analysis import load_source_data, prepare_data, make_summary, build_rfm, make_charts
from .database import create_database


def run() -> dict:
    raw, source = load_source_data(ROOT_DIR)
    sales, quality = prepare_data(raw)
    rfm = build_rfm(sales)
    summary = make_summary(sales)
    sales.to_csv(PROCESSED_DIR / "cleaned_sales.csv", index=False)
    rfm.to_csv(PROCESSED_DIR / "customer_rfm.csv", index=False)
    (OUTPUT_DIR / "summary.json").write_text(json.dumps({"source": source, "quality": quality, "summary": summary}, indent=2), encoding="utf-8")
    create_database(DB_PATH, sales)
    charts = make_charts(sales, rfm, CHART_DIR)
    print("\nSALES LENS ANALYSIS COMPLETE")
    print("Dataset:", source)
    print("Rows analysed:", len(sales))
    print("Revenue: £{:,.2f}".format(summary["total_revenue_gbp"]))
    print("Invoices:", summary["invoices"])
    print("Customers with ID:", summary["customers_with_id"])
    print("Database:", DB_PATH)
    print("Charts saved:", len(charts))
    if "SYNTHETIC" in source:
        print("NOTE: These figures come from a synthetic demo sample, not UCI's original dataset.")
    return {"source":source,"quality":quality,"summary":summary,"charts":charts}

if __name__ == "__main__":
    run()
