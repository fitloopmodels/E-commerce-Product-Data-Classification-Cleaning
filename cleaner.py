"""
cleaner.py
----------
Handles all data cleaning operations:
  1. Remove junk / placeholder values  → standardize to None
  2. Strip and normalize whitespace
  3. Deduplicate records (exact + near-duplicate by SKU)
  4. Handle missing values (fill where deterministic, flag where not)
  5. Standardize price, stock, rating fields
  6. Normalize common fields (color, size)

Returns a cleaned DataFrame with a `cleaning_notes` column explaining
what was changed for each record.
"""

import re
import pandas as pd
import numpy as np
from typing import Optional


# Values that should be treated as missing
JUNK_SENTINEL = {
    "n/a", "na", "tbd", "???", "unknown", "-", "null",
    "none", "not available", "not applicable", "", "nan"
}


class DataCleaner:

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df["cleaning_notes"] = ""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> pd.DataFrame:
        print("[Cleaner] Starting cleaning pipeline ...")
        self._normalize_whitespace()
        self._nullify_junk_values()
        self._remove_exact_duplicates()
        self._remove_near_duplicates()
        self._clean_price()
        self._clean_stock()
        self._clean_rating()
        self._normalize_color()
        self._normalize_size()
        self._normalize_category_casing()
        self._flag_missing_critical_fields()
        print(f"[Cleaner] Done. {len(self.df)} records remain after cleaning.")
        return self.df

    # ------------------------------------------------------------------
    # Step implementations
    # ------------------------------------------------------------------

    def _normalize_whitespace(self):
        """Strip leading/trailing whitespace from all string columns."""
        str_cols = self.df.select_dtypes(include=["object", "string"]).columns
        for col in str_cols:
            self.df[col] = self.df[col].apply(
                lambda x: re.sub(r"\s+", " ", x.strip()) if isinstance(x, str) else x
            )

    def _nullify_junk_values(self):
        """Replace placeholder strings with np.nan."""
        str_cols = self.df.select_dtypes(include=["object", "string"]).columns
        count = 0
        for col in str_cols:
            if col == "cleaning_notes":
                continue
            mask = self.df[col].apply(
                lambda x: isinstance(x, str) and x.strip().lower() in JUNK_SENTINEL
            )
            count += mask.sum()
            self.df.loc[mask, col] = np.nan
            self.df.loc[mask, "cleaning_notes"] = (
                self.df.loc[mask, "cleaning_notes"] + f"nullified junk in '{col}'; "
            )
        print(f"  [Cleaner] Nullified {count} junk values across columns.")

    def _remove_exact_duplicates(self):
        """Drop records that are identical on all columns except product_id."""
        before = len(self.df)
        subset = [c for c in self.df.columns if c not in ("product_id", "cleaning_notes")]
        self.df = self.df.drop_duplicates(subset=subset, keep="first").reset_index(drop=True)
        removed = before - len(self.df)
        print(f"  [Cleaner] Removed {removed} exact duplicate records.")

    def _remove_near_duplicates(self):
        """
        Keep the first occurrence of each SKU.
        Near-duplicates often share SKU but differ by trivial whitespace.
        """
        before = len(self.df)
        self.df["_sku_norm"] = self.df["sku"].str.strip().str.upper()
        self.df = self.df.drop_duplicates(subset=["_sku_norm"], keep="first").reset_index(drop=True)
        self.df.drop(columns=["_sku_norm"], inplace=True)
        removed = before - len(self.df)
        print(f"  [Cleaner] Removed {removed} near-duplicate records (by SKU).")

    def _clean_price(self):
        """Coerce price to float. Flag non-positive prices."""
        self.df["price"] = pd.to_numeric(self.df["price"], errors="coerce")
        bad_mask = (self.df["price"] <= 0) & self.df["price"].notna()
        self.df.loc[bad_mask, "price"] = np.nan
        self.df.loc[bad_mask, "cleaning_notes"] += "invalid price set to null; "

    def _clean_stock(self):
        """Coerce stock_quantity to int. Negative → 0."""
        self.df["stock_quantity"] = pd.to_numeric(self.df["stock_quantity"], errors="coerce")
        neg_mask = self.df["stock_quantity"] < 0
        self.df.loc[neg_mask, "stock_quantity"] = 0
        self.df.loc[neg_mask, "cleaning_notes"] += "negative stock corrected to 0; "
        self.df["stock_quantity"] = self.df["stock_quantity"].astype("Int64")

    def _clean_rating(self):
        """Coerce rating to float. Clamp to [1, 5]."""
        self.df["rating"] = pd.to_numeric(self.df["rating"], errors="coerce")
        hi_mask = self.df["rating"] > 5
        lo_mask = self.df["rating"] < 1
        self.df.loc[hi_mask, "rating"] = 5.0
        self.df.loc[lo_mask, "rating"] = 1.0
        self.df.loc[hi_mask | lo_mask, "cleaning_notes"] += "rating clamped; "

    def _normalize_color(self):
        """Title-case color values."""
        self.df["color"] = self.df["color"].apply(
            lambda x: x.title() if isinstance(x, str) else x
        )

    def _normalize_size(self):
        """
        Standardize size tokens:
          - 'uk 8' → 'UK 8'
          - '300 ml' / '300ML' → '300ml'
          - 's' / 'small' → 'S'
        """
        size_map = {
            "small": "S", "medium": "M", "large": "L",
            "extra large": "XL", "extra small": "XS",
            "double extra large": "XXL", "triple extra large": "XXXL",
        }

        def _std_size(val):
            if not isinstance(val, str):
                return val
            val = val.strip()
            lower = val.lower()
            if lower in size_map:
                return size_map[lower]
            # Normalize UK shoe size
            val = re.sub(r"(?i)\buk[-\s]?(\d+)\b", r"UK \1", val)
            val = re.sub(r"(?i)\beu[-\s]?(\d+)\b", r"EU \1", val)
            # Normalize volume/weight units
            val = re.sub(r"(?i)(\d+)\s*(ml)\b", r"\1ml", val)
            val = re.sub(r"(?i)(\d+)\s*(l)\b", r"\1L", val)
            val = re.sub(r"(?i)(\d+)\s*(g)\b", r"\1g", val)
            val = re.sub(r"(?i)(\d+)\s*(kg)\b", r"\1kg", val)
            return val.strip()

        self.df["size"] = self.df["size"].apply(_std_size)

    def _normalize_category_casing(self):
        """Title-case category and subcategory."""
        for col in ("category", "subcategory", "brand"):
            self.df[col] = self.df[col].apply(
                lambda x: x.strip().title() if isinstance(x, str) else x
            )

    def _flag_missing_critical_fields(self):
        """Add flags for records that are missing critical attributes."""
        critical = ["product_name", "sku", "price"]
        for field in critical:
            mask = self.df[field].isna()
            self.df.loc[mask, "cleaning_notes"] += f"missing critical field '{field}'; "

        self.df["has_missing_critical"] = (
            self.df[critical].isna().any(axis=1)
        )


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience wrapper used by the pipeline."""
    return DataCleaner(df).run()
