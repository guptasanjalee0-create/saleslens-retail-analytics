"""SQLite storage so the project runs without a separate database server."""
import sqlite3
from pathlib import Path
import pandas as pd


def create_database(db_path: Path, sales: pd.DataFrame) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript("""
        DROP TABLE IF EXISTS retail_transactions;
        CREATE TABLE retail_transactions (
            transaction_row_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT NOT NULL,
            stock_code TEXT NOT NULL,
            description TEXT,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            invoice_date TEXT NOT NULL,
            unit_price REAL NOT NULL CHECK(unit_price > 0),
            customer_id INTEGER,
            country TEXT,
            revenue REAL NOT NULL CHECK(revenue >= 0),
            invoice_month TEXT NOT NULL,
            invoice_hour INTEGER NOT NULL
        );
        CREATE INDEX idx_transactions_invoice ON retail_transactions(invoice_no);
        CREATE INDEX idx_transactions_product ON retail_transactions(stock_code);
        CREATE INDEX idx_transactions_customer ON retail_transactions(customer_id);
        CREATE INDEX idx_transactions_date ON retail_transactions(invoice_date);
        """)
        out=sales[["InvoiceNo","StockCode","Description","Quantity","InvoiceDate","UnitPrice","CustomerID","Country","Revenue","InvoiceMonth","InvoiceHour"]].copy()
        out.columns=["invoice_no","stock_code","description","quantity","invoice_date","unit_price","customer_id","country","revenue","invoice_month","invoice_hour"]
        out["invoice_date"] = pd.to_datetime(out["invoice_date"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        out["customer_id"] = out["customer_id"].astype("Int64").astype(object).where(out["customer_id"].notna(), None)
        out.to_sql("retail_transactions",conn,if_exists="append",index=False)
