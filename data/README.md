# Dataset instructions

## Immediate demo

The repository includes `sample/online_retail_sample.csv`. This is a **synthetic demonstration dataset** with the same column names as UCI Online Retail. It lets you run and test the project immediately, but it must not be presented as real-world UCI data.

## Full official dataset

1. Open the [UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail).
2. Download `Online Retail.xlsx`.
3. Place it at `data/raw/Online Retail.xlsx`.
4. Run `python run_analysis.py` again.

Alternatively install `ucimlrepo` (included in `requirements.txt`) and run:

```bash
python download_dataset.py
```

The downloader writes `data/raw/online_retail.csv`.

The full UCI dataset has 541,909 transaction rows and covers 1 December 2010 to 9 December 2011. Dataset: Chen, D. (2015). *Online Retail*. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33. Licensed under CC BY 4.0. Cite the dataset and retain attribution in any public reuse.
