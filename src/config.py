from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
SAMPLE_DATA = DATA_DIR / "sample" / "online_retail_sample.csv"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = ROOT_DIR / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"
DB_PATH = DATA_DIR / "saleslens.sqlite"

for folder in (PROCESSED_DIR, OUTPUT_DIR, CHART_DIR):
    folder.mkdir(parents=True, exist_ok=True)
