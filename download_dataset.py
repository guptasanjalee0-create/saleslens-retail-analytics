"""Download UCI Online Retail through the official ucimlrepo package.
Run: python download_dataset.py
"""
from pathlib import Path
import sys
import pandas as pd

ROOT=Path(__file__).resolve().parent
RAW=ROOT/"data"/"raw"
RAW.mkdir(parents=True,exist_ok=True)
try:
    from ucimlrepo import fetch_ucirepo
except ImportError:
    print("Install the optional downloader first: pip install ucimlrepo")
    sys.exit(1)
print("Fetching UCI Online Retail dataset (ID 352)...")
dataset=fetch_ucirepo(id=352)
# UCI's full data are exposed as a dataframe. Save the source attributes and target.
# Prefer the original combined table when the UCI API exposes it.
data = getattr(dataset.data, "original", None)
if data is None:
    parts = []
    for field in ("ids", "features", "targets"):
        part = getattr(dataset.data, field, None)
        if part is not None and not part.empty:
            parts.append(part)
    if not parts:
        raise RuntimeError("The UCI API returned no tabular data.")
    data = pd.concat(parts, axis=1)
else:
    data = data.copy()
# Preserve expected UCI field names and write local workbook-like CSV for easy loading.
out=RAW/"online_retail.csv"
data.to_csv(out,index=False)
print(f"Saved {len(data):,} rows to {out}")
print("Now run: python run_analysis.py")
