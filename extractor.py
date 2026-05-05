"""
extractor.py
------------
Extracts structured product attributes from the raw product_name field
using regular expressions and known brand/taxonomy lookup.

Attributes extracted:
  - extracted_brand     : brand token found in product name
  - extracted_size      : size/volume/weight token (e.g. "256GB", "5L", "XL")
  - extracted_color     : color token
  - extracted_model     : model number / product code pattern
  - extracted_ram       : RAM spec (electronics)
  - extracted_storage   : Storage spec (electronics)
  - name_cleaned        : product name after stripping extracted tokens (normalized)
"""

import re
import json
from pathlib import Path
from typing import Optional
import pandas as pd


# ------------------------------------------------------------------
# Regex patterns
# ------------------------------------------------------------------

# Storage: 32GB, 128 GB, 512GB, 1TB, 2 TB
RE_STORAGE = re.compile(
    r"\b(\d+)\s*(GB|TB|gb|tb)\b(?!\s*RAM|\s*ram)", re.IGNORECASE
)

# RAM: 8GB RAM, 16 GB RAM, 6GB RAM
RE_RAM = re.compile(r"\b(\d+)\s*GB\s*RAM\b", re.IGNORECASE)

# Volume/Weight: 250ml, 5L, 300 ml, 2kg, 80g, 500 mL
# Note: no lookahead here; we rely on context (L for litre only when preceded by digits)
RE_VOLUME = re.compile(r"\b(\d+\.?\d*)\s*(ml|mL|l|L|kg|g|mg)\b")

# Apparel size: standalone S/M/L/XL/XXL/XXXL/XS
RE_APPAREL_SIZE = re.compile(r"\b(XS|S|M|L|XL|XXL|XXXL|XXXXL)\b")

# Shoe size: UK 9, US 10, EU 42
RE_SHOE_SIZE = re.compile(r"\b(UK|US|EU)\s*-?\s*(\d+\.?\d*)\b", re.IGNORECASE)

# Inch display: 55", 15.6 inch, 13-inch
RE_INCH = re.compile(r'(\d+\.?\d*)\s*[""″]?\s*(?:inch|in\b|")', re.IGNORECASE)

# Model/code: mix of letters+digits like "WH-1000XM5", "HL7756", "200D"
RE_MODEL = re.compile(r"\b([A-Z]{1,4}[-_]?\d{3,6}[A-Z0-9]*)\b")

# Color tokens (common list)
COLOR_TOKENS = {
    "black", "white", "blue", "red", "green", "grey", "gray", "silver",
    "gold", "rose gold", "pink", "yellow", "orange", "purple", "violet",
    "brown", "beige", "navy", "maroon", "teal", "cyan", "olive",
    "multicolor", "multi-color", "natural", "transparent", "cream",
    "midnight", "emerald", "titanium", "platinum", "charcoal", "coral",
    "lavender", "peach", "mint", "tan", "camel",
}

# ------------------------------------------------------------------
# Brand extraction
# ------------------------------------------------------------------

def _load_known_brands(taxonomy_path: str) -> set:
    """Build a flat set of known brand names from the taxonomy brands pool."""
    # We read from data_generator indirectly — just hardcode the union.
    return {
        "samsung", "apple", "sony", "oneplus", "realme", "xiaomi", "boat",
        "jbl", "bose", "canon", "nikon", "lg", "dell", "hp", "lenovo",
        "asus", "acer", "motorola", "nike", "adidas", "puma", "reebok",
        "h&m", "zara", "allen solly", "van heusen", "levis", "wrangler",
        "ucb", "roadster", "bata", "skechers", "woodland", "red tape",
        "liberty", "prestige", "hawkins", "bajaj", "philips", "bosch",
        "inalsa", "pigeon", "cello", "tupperware", "ikea", "lakme",
        "maybelline", "loreal", "himalaya", "biotique", "neutrogena",
        "nivea", "dove", "wow", "mamaearth", "decathlon", "cosco",
        "sg", "mrf", "boldfit", "strauss", "penguin", "harpercollins",
        "oxford", "scholastic", "classmate", "reynolds", "hasbro",
        "mattel", "lego", "fisher-price", "funskool", "skoodle",
        "nivia", "anker", "zebronics",
    }


KNOWN_BRANDS = _load_known_brands("")


def _extract_brand(name: str, existing_brand) -> Optional[str]:
    """Try to find a brand in the product name if existing brand is missing."""
    if pd.notna(existing_brand) and str(existing_brand).strip():
        return str(existing_brand).strip().title()
    if not isinstance(name, str):
        return None
    lower = name.lower()
    for brand in sorted(KNOWN_BRANDS, key=len, reverse=True):
        if brand in lower:
            return brand.title()
    return None


# ------------------------------------------------------------------
# Main extractor class
# ------------------------------------------------------------------

class AttributeExtractor:

    def extract_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        print("[Extractor] Extracting attributes from product names ...")
        extracted = df.apply(self._extract_row, axis=1, result_type="expand")
        for col in extracted.columns:
            df[col] = extracted[col]
        print(f"  [Extractor] Done. Extracted attributes for {len(df)} records.")
        return df

    def _extract_row(self, row: pd.Series) -> dict:
        name = row.get("product_name", "")
        name = str(name) if pd.notna(name) else ""

        # --- RAM (must extract before storage to avoid overlap) ---
        ram_match = RE_RAM.search(name)
        ram = f"{ram_match.group(1)}GB RAM" if ram_match else None

        # --- Storage (after excluding RAM match) ---
        # RE_STORAGE already has a negative lookahead for " RAM", so first
        # match is safe to use directly without a secondary window check.
        storage = None
        for m in RE_STORAGE.finditer(name):
            storage = f"{m.group(1)}{m.group(2).upper()}"
            break

        # --- Volume / Weight ---
        size_from_volume = None
        vol_match = RE_VOLUME.search(name)
        if vol_match:
            size_from_volume = f"{vol_match.group(1)}{vol_match.group(2).lower()}"

        # --- Apparel size ---
        apparel_match = RE_APPAREL_SIZE.search(name)
        apparel_size = apparel_match.group(1).upper() if apparel_match else None

        # --- Shoe size ---
        shoe_match = RE_SHOE_SIZE.search(name)
        shoe_size = f"{shoe_match.group(1).upper()} {shoe_match.group(2)}" if shoe_match else None

        # --- Screen size ---
        inch_match = RE_INCH.search(name)
        inch_size = f'{inch_match.group(1)}"' if inch_match else None

        # Aggregate size (priority: storage > volume > apparel > shoe > inch)
        extracted_size = (
            row.get("size")
            if pd.notna(row.get("size"))
            else (storage or size_from_volume or apparel_size or shoe_size or inch_size)
        )

        # --- Model number ---
        model_match = RE_MODEL.search(name)
        model = model_match.group(1) if model_match else None

        # --- Color ---
        color = row.get("color")
        if pd.isna(color) or not str(color).strip():
            name_lower = name.lower()
            for token in COLOR_TOKENS:
                if re.search(r"\b" + re.escape(token) + r"\b", name_lower):
                    color = token.title()
                    break
            else:
                color = None

        # --- Brand ---
        extracted_brand = _extract_brand(name, row.get("brand"))

        # --- Clean name: lowercase, remove extra whitespace ---
        name_cleaned = re.sub(r"\s+", " ", name.strip().lower())

        return {
            "extracted_brand": extracted_brand,
            "extracted_ram": ram,
            "extracted_storage": storage,
            "extracted_size": extracted_size,
            "extracted_color": color,
            "extracted_model": model,
            "name_cleaned": name_cleaned,
        }


def extract(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience wrapper used by the pipeline."""
    return AttributeExtractor().extract_dataframe(df)
