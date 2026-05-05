"""
pipeline.py
-----------
Orchestrates the full ETL pipeline:

  1. Load raw CSV  (or generate synthetic data)
  2. Clean         → cleaner.py
  3. Classify      → classifier.py
  4. Extract attrs → extractor.py
  5. Quality check → quality_checker.py
  6. Save outputs  → data/processed/

Usage:
  from src.pipeline import Pipeline
  Pipeline().run()
"""

import os
import json
import time
from pathlib import Path

import pandas as pd

from src.data_generator import generate_records, save_to_csv
from src.cleaner import clean
from src.classifier import classify
from src.extractor import extract
from src.quality_checker import check


RAW_PATH       = "data/raw/products_raw.csv"
PROCESSED_PATH = "data/processed/products_cleaned.csv"
REPORT_PATH    = "reports/quality_report.json"
POOR_PATH      = "data/processed/products_poor_quality.csv"
TAXONOMY_PATH  = "data/taxonomy/taxonomy.json"


class Pipeline:

    def __init__(
        self,
        raw_path: str = RAW_PATH,
        taxonomy_path: str = TAXONOMY_PATH,
        generate_if_missing: bool = True,
        n_records: int = 1200,
    ):
        self.raw_path = raw_path
        self.taxonomy_path = taxonomy_path
        self.generate_if_missing = generate_if_missing
        self.n_records = n_records

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(self) -> pd.DataFrame:
        t0 = time.time()
        print("\n" + "=" * 56)
        print("  E-COMMERCE PRODUCT CLASSIFICATION PIPELINE")
        print("=" * 56)

        # STEP 1 – Load / generate raw data
        df_raw = self._load_raw()
        print(f"\nSTEP 1 ✓ Loaded {len(df_raw)} raw records from '{self.raw_path}'")

        # STEP 2 – Clean
        print("\nSTEP 2 – Cleaning data ...")
        df_clean = clean(df_raw)
        print(f"STEP 2 ✓ {len(df_clean)} records after cleaning")

        # STEP 3 – Classify
        print("\nSTEP 3 – Classifying products ...")
        df_classified = classify(df_clean, taxonomy_path=self.taxonomy_path)
        print("STEP 3 ✓ Classification complete")

        # STEP 4 – Extract attributes
        print("\nSTEP 4 – Extracting attributes ...")
        df_extracted = extract(df_classified)
        print("STEP 4 ✓ Attribute extraction complete")

        # STEP 5 – Quality check
        print("\nSTEP 5 – Running quality checks ...")
        df_final, report = check(df_extracted)
        print("STEP 5 ✓ Quality checks complete")

        # STEP 6 – Save outputs
        print("\nSTEP 6 – Saving outputs ...")
        self._save_outputs(df_final, report)
        print("STEP 6 ✓ Outputs saved")

        elapsed = time.time() - t0
        print(f"\n Pipeline completed in {elapsed:.2f}s\n")
        return df_final

    # ------------------------------------------------------------------

    def _load_raw(self) -> pd.DataFrame:
        if not os.path.exists(self.raw_path):
            if self.generate_if_missing:
                print(f"[Pipeline] '{self.raw_path}' not found — generating {self.n_records} records ...")
                records = generate_records(n=self.n_records)
                save_to_csv(records, self.raw_path)
            else:
                raise FileNotFoundError(
                    f"Raw data file not found: {self.raw_path}. "
                    "Set generate_if_missing=True to auto-generate."
                )
        return pd.read_csv(self.raw_path, dtype=str, keep_default_na=False)

    def _save_outputs(self, df: pd.DataFrame, report: dict):
        os.makedirs("data/processed", exist_ok=True)
        os.makedirs("reports", exist_ok=True)

        # Full cleaned + enriched dataset
        df.to_csv(PROCESSED_PATH, index=False)
        print(f"  Saved full dataset      → {PROCESSED_PATH}")

        # Separate file for POOR quality records (for manual review)
        poor = df[df["quality_tier"] == "POOR"]
        if not poor.empty:
            poor.to_csv(POOR_PATH, index=False)
            print(f"  Saved poor-quality rows → {POOR_PATH} ({len(poor)} records)")

        # Quality report JSON
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"  Saved quality report    → {REPORT_PATH}")

        # Summary stats to stdout
        print(f"\n  Column summary of processed data:")
        for col in df.columns:
            null_count = df[col].isna().sum()
            print(f"    {col:<35} nulls: {null_count}")
