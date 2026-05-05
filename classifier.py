"""
classifier.py
-------------
Rule-based product classifier using keyword matching against a taxonomy.

Strategy:
  1. Load the taxonomy JSON (category → subcategory → keyword list).
  2. For each product, build a search corpus from name + subcategory + brand.
  3. Score every (category, subcategory) pair by keyword hit count.
  4. Assign the pair with the highest score.
  5. Fall back to existing category/subcategory if score is zero and they
     already look valid.
  6. Record confidence score and match reason for auditability.
"""

import json
import re
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
import numpy as np


class ProductClassifier:

    def __init__(self, taxonomy_path: str = "data/taxonomy/taxonomy.json"):
        with open(taxonomy_path, "r", encoding="utf-8") as f:
            self.taxonomy = json.load(f)
        # Pre-build a flat list: [(category, subcategory, [keywords])]
        self._flat = self._flatten_taxonomy()
        self._valid_categories = set(self.taxonomy.keys())
        self._valid_subcategories = {
            sub
            for cat in self.taxonomy.values()
            for sub in cat["subcategories"].keys()
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        print("[Classifier] Running classification ...")
        results = df.apply(self._classify_row, axis=1, result_type="expand")
        df["classified_category"] = results["category"]
        df["classified_subcategory"] = results["subcategory"]
        df["classification_confidence"] = results["confidence"]
        df["classification_reason"] = results["reason"]
        classified = df["classified_category"].notna().sum()
        print(
            f"  [Classifier] Classified {classified}/{len(df)} records "
            f"({classified / len(df) * 100:.1f}%)"
        )
        return df

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _flatten_taxonomy(self):
        flat = []
        for category, data in self.taxonomy.items():
            for subcategory, sub_data in data["subcategories"].items():
                flat.append((category, subcategory, sub_data["keywords"]))
        return flat

    def _build_corpus(self, row: pd.Series) -> str:
        """Combine text fields into a single lowercase search string."""
        parts = [
            row.get("product_name", ""),
            row.get("subcategory", ""),
            row.get("brand", ""),
            row.get("color", ""),
        ]
        corpus = " ".join(str(p) for p in parts if pd.notna(p) and p)
        return corpus.lower()

    def _score(self, corpus: str, keywords: list) -> int:
        """Count how many keywords appear in the corpus."""
        score = 0
        for kw in keywords:
            # Whole-word match where possible
            pattern = r"\b" + re.escape(kw.lower()) + r"\b"
            if re.search(pattern, corpus):
                score += 1
        return score

    def _classify_row(self, row: pd.Series) -> dict:
        corpus = self._build_corpus(row)

        # Check if existing category is already valid — use as tie-breaker
        existing_cat = row.get("category")
        existing_cat_valid = (
            isinstance(existing_cat, str)
            and existing_cat.strip().title() in self._valid_categories
        )

        best_score = 0
        best_cat = None
        best_sub = None

        for (category, subcategory, keywords) in self._flat:
            s = self._score(corpus, keywords)
            if s > best_score:
                best_score = s
                best_cat = category
                best_sub = subcategory
            elif s == best_score and s > 0 and existing_cat_valid:
                # Prefer matching the existing category on tie
                if category == existing_cat.strip().title():
                    best_cat = category
                    best_sub = subcategory

        if best_score == 0:
            # No keyword match at all
            if existing_cat_valid:
                return {
                    "category": existing_cat.strip().title(),
                    "subcategory": None,
                    "confidence": "low",
                    "reason": "existing_category_fallback",
                }
            return {
                "category": None,
                "subcategory": None,
                "confidence": "none",
                "reason": "no_match",
            }

        confidence = (
            "high" if best_score >= 3
            else "medium" if best_score == 2
            else "low"
        )

        return {
            "category": best_cat,
            "subcategory": best_sub,
            "confidence": confidence,
            "reason": f"keyword_match(score={best_score})",
        }


def classify(df: pd.DataFrame, taxonomy_path: str = "data/taxonomy/taxonomy.json") -> pd.DataFrame:
    """Convenience wrapper used by the pipeline."""
    return ProductClassifier(taxonomy_path).classify_dataframe(df)
