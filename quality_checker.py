"""
quality_checker.py
------------------
Runs a suite of data quality checks on the processed DataFrame and produces:
  - A per-record quality score (0–100)
  - A quality_tier label: GOOD / ACCEPTABLE / POOR
  - A quality_issues list (human-readable flags per record)
  - An aggregate QA report (printed + returned as dict)

Quality dimensions checked:
  1. Completeness  – critical and optional fields populated
  2. Consistency   – price ranges, rating bounds, valid category
  3. Validity      – SKU format, price > 0
  4. Classification coverage – classified_category is not null
  5. Search relevance – name_cleaned is meaningful (not too short)
"""

import re
from typing import Tuple
import pandas as pd
import numpy as np


# ------------------------------------------------------------------
# Field weights for quality score
# ------------------------------------------------------------------

FIELD_WEIGHTS = {
    # (field_name, weight, required)
    "product_name":          (10, True),
    "sku":                   (10, True),
    "price":                 (10, True),
    "classified_category":   (10, True),
    "classified_subcategory":(5,  False),
    "extracted_brand":       (8,  False),
    "extracted_size":        (7,  False),
    "extracted_color":       (5,  False),
    "extracted_model":       (4,  False),
    "rating":                (3,  False),
    "stock_quantity":        (5,  False),
    "created_at":            (3,  False),
}

VALID_CATEGORIES = {
    "Electronics", "Clothing", "Footwear",
    "Home & Kitchen", "Beauty & Personal Care",
    "Sports & Fitness", "Books & Stationery", "Toys & Games"
}

SKU_PATTERN = re.compile(r"^SKU-\d{5}$")

PRICE_RANGES = {
    "Electronics":             (50,    200000),
    "Clothing":                (50,    50000),
    "Footwear":                (50,    50000),
    "Home & Kitchen":          (50,    100000),
    "Beauty & Personal Care":  (20,    20000),
    "Sports & Fitness":        (50,    100000),
    "Books & Stationery":      (20,    5000),
    "Toys & Games":            (50,    50000),
}


class QualityChecker:

    def check(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        print("[QualityChecker] Running quality checks ...")
        scores = []
        issues_list = []

        for _, row in df.iterrows():
            score, issues = self._score_row(row)
            scores.append(score)
            issues_list.append("; ".join(issues) if issues else "OK")

        df["quality_score"] = scores
        df["quality_issues"] = issues_list
        df["quality_tier"] = df["quality_score"].apply(self._tier)

        report = self._build_report(df)
        self._print_report(report)
        return df, report

    # ------------------------------------------------------------------

    def _score_row(self, row: pd.Series) -> Tuple[int, list]:
        issues = []
        total_weight = sum(w for (w, _) in FIELD_WEIGHTS.values())
        earned = 0

        for field, (weight, required) in FIELD_WEIGHTS.items():
            value = row.get(field)
            is_present = pd.notna(value) and str(value).strip() not in ("", "None", "nan")
            if is_present:
                earned += weight
            elif required:
                issues.append(f"missing_required:{field}")

        # Bonus / penalty checks
        # 1. Valid category
        cat = row.get("classified_category")
        if pd.notna(cat) and cat not in VALID_CATEGORIES:
            earned -= 5
            issues.append(f"invalid_category:{cat}")

        # 2. Price in expected range for category
        price = row.get("price")
        if pd.notna(price) and pd.notna(cat) and cat in PRICE_RANGES:
            lo, hi = PRICE_RANGES[cat]
            if not (lo <= price <= hi):
                earned -= 5
                issues.append(f"price_out_of_range:{price}")

        # 3. SKU format
        sku = row.get("sku")
        if pd.notna(sku) and not SKU_PATTERN.match(str(sku).strip()):
            earned -= 3
            issues.append(f"invalid_sku_format:{sku}")

        # 4. Rating bounds
        rating = row.get("rating")
        if pd.notna(rating):
            if not (1.0 <= float(rating) <= 5.0):
                earned -= 3
                issues.append(f"rating_out_of_bounds:{rating}")

        # 5. Name too short (< 5 chars after cleaning)
        name = row.get("name_cleaned", "")
        if isinstance(name, str) and len(name.strip()) < 5:
            earned -= 5
            issues.append("name_too_short")

        # 6. Low classification confidence
        conf = row.get("classification_confidence")
        if conf == "low":
            earned -= 3
            issues.append("low_classification_confidence")
        elif conf == "none":
            earned -= 8
            issues.append("unclassified")

        score = max(0, min(100, int((earned / total_weight) * 100)))
        return score, issues

    def _tier(self, score: int) -> str:
        if score >= 75:
            return "GOOD"
        elif score >= 45:
            return "ACCEPTABLE"
        return "POOR"

    def _build_report(self, df: pd.DataFrame) -> dict:
        total = len(df)
        tier_counts = df["quality_tier"].value_counts().to_dict()

        return {
            "total_records": total,
            "quality_tier_distribution": tier_counts,
            "avg_quality_score": round(df["quality_score"].mean(), 2),
            "classification_rate_pct": round(
                df["classified_category"].notna().sum() / total * 100, 2
            ),
            "missing_price_pct": round(df["price"].isna().sum() / total * 100, 2),
            "missing_brand_pct": round(
                df["extracted_brand"].isna().sum() / total * 100, 2
            ),
            "missing_size_pct": round(
                df["extracted_size"].isna().sum() / total * 100, 2
            ),
            "high_confidence_pct": round(
                (df["classification_confidence"] == "high").sum() / total * 100, 2
            ),
            "low_confidence_pct": round(
                (df["classification_confidence"] == "low").sum() / total * 100, 2
            ),
            "unclassified_pct": round(
                (df["classification_confidence"] == "none").sum() / total * 100, 2
            ),
            "records_with_critical_missing": int(
                df.get("has_missing_critical", pd.Series([False] * total)).sum()
            ),
        }

    def _print_report(self, r: dict):
        print("\n" + "=" * 56)
        print("  DATA QUALITY REPORT")
        print("=" * 56)
        print(f"  Total records          : {r['total_records']}")
        print(f"  Avg quality score      : {r['avg_quality_score']} / 100")
        tiers = r["quality_tier_distribution"]
        print(f"  GOOD (>=75)            : {tiers.get('GOOD', 0)}")
        print(f"  ACCEPTABLE (45-74)     : {tiers.get('ACCEPTABLE', 0)}")
        print(f"  POOR (<45)             : {tiers.get('POOR', 0)}")
        print(f"  Classification rate    : {r['classification_rate_pct']}%")
        print(f"  High confidence        : {r['high_confidence_pct']}%")
        print(f"  Low confidence         : {r['low_confidence_pct']}%")
        print(f"  Unclassified           : {r['unclassified_pct']}%")
        print(f"  Missing price          : {r['missing_price_pct']}%")
        print(f"  Missing brand          : {r['missing_brand_pct']}%")
        print(f"  Missing size           : {r['missing_size_pct']}%")
        print(f"  Records w/ critical ∅  : {r['records_with_critical_missing']}")
        print("=" * 56 + "\n")


def check(df: pd.DataFrame):
    """Convenience wrapper used by the pipeline."""
    return QualityChecker().check(df)
