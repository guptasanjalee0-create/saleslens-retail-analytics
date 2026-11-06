from pathlib import Path
import pandas as pd
from src.analysis import prepare_data, build_rfm


def sample():
    return pd.DataFrame([
        ["1001","A1","Item A",2,"12/01/2011 10:00",5.0,12345,"United Kingdom"],
        ["1001","B1","Item B",1,"12/01/2011 10:00",3.0,12345,"United Kingdom"],
        ["C1002","A1","Item A",-1,"12/02/2011 10:00",5.0,12345,"United Kingdom"],
        ["1003","A1","Item A",0,"12/03/2011 10:00",5.0,12346,"France"],
        ["1004","C1","Item C",1,"12/04/2011 10:00",0,12347,"France"],
    ], columns=["InvoiceNo","StockCode","Description","Quantity","InvoiceDate","UnitPrice","CustomerID","Country"])


def test_prepare_data_excludes_cancellations_and_invalid_rows():
    clean, metrics = prepare_data(sample())
    assert len(clean) == 2
    assert round(clean["Revenue"].sum(), 2) == 13.0
    assert metrics["cancellation_rows_excluded"] == 1


def test_rfm_has_expected_columns_and_segment():
    clean, _ = prepare_data(sample())
    rfm = build_rfm(clean)
    assert {"CustomerID","RecencyDays","Frequency","Monetary","Segment"}.issubset(rfm.columns)
    assert len(rfm) == 1
    assert rfm.iloc[0]["Frequency"] == 1
