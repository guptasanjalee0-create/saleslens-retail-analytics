import sqlite3
from pathlib import Path
import pandas as pd
from src.analysis import prepare_data
from src.database import create_database


def test_database_loads_clean_sales(tmp_path):
    raw = pd.DataFrame([
        ["1001", "A1", "Item A", 2, "12/01/2011 10:00", 5.0, 12345, "United Kingdom"],
        ["1002", "B1", "Item B", 1, "12/02/2011 11:00", 3.0, 12346, "France"],
    ], columns=["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"])
    sales, _ = prepare_data(raw)
    db_path = tmp_path / "saleslens.sqlite"
    create_database(db_path, sales)
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM retail_transactions").fetchone()[0]
        revenue = conn.execute("SELECT ROUND(SUM(revenue), 2) FROM retail_transactions").fetchone()[0]
    assert count == 2
    assert revenue == 13.0
