-- SalesLens SQLite schema. The Python pipeline creates this table automatically.
CREATE TABLE IF NOT EXISTS retail_transactions (
    transaction_row_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no TEXT NOT NULL,
    stock_code TEXT NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    invoice_date TEXT NOT NULL,
    unit_price REAL NOT NULL CHECK (unit_price > 0),
    customer_id INTEGER,
    country TEXT,
    revenue REAL NOT NULL CHECK (revenue >= 0),
    invoice_month TEXT NOT NULL,
    invoice_hour INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_transactions_invoice ON retail_transactions(invoice_no);
CREATE INDEX IF NOT EXISTS idx_transactions_product ON retail_transactions(stock_code);
CREATE INDEX IF NOT EXISTS idx_transactions_customer ON retail_transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON retail_transactions(invoice_date);
