# E-commerce Product Data Classification & Cleaning

A production-grade Python pipeline that ingests raw, messy e-commerce product records, cleans them, classifies them into a structured taxonomy, extracts key attributes, and scores each record for data quality.

Built as a portfolio project demonstrating real-world data engineering skills: rule-based NLP, ETL design, modular architecture, and test-driven development.

---

## What it does

| Step | Module | What happens |
|------|--------|--------------|
| 1 | `data_generator.py` | Generates 1200+ realistic, intentionally messy product records |
| 2 | `cleaner.py` | Removes duplicates, nullifies junk values, standardizes fields |
| 3 | `classifier.py` | Classifies products into a taxonomy using keyword scoring |
| 4 | `extractor.py` | Extracts brand, size, RAM, storage, color, model from product names |
| 5 | `quality_checker.py` | Scores each record 0–100 and labels it GOOD / ACCEPTABLE / POOR |
| 6 | `pipeline.py` | Orchestrates all steps and saves outputs |

**Results on 1200 records:**
- 98%+ classification rate
- Removes ~8% exact/near duplicates automatically
- Nullifies 1600+ junk placeholder values ("N/A", "TBD", "???", etc.)
- Final output: 28-column enriched CSV with quality scores

---

## Project structure

```
ecommerce-classifier/
├── main.py                         # CLI entry point
├── requirements.txt
├── setup.py
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── data_generator.py           # Synthetic data generation
│   ├── cleaner.py                  # Data cleaning pipeline
│   ├── classifier.py               # Rule-based taxonomy classifier
│   ├── extractor.py                # Regex attribute extraction
│   ├── quality_checker.py          # Quality scoring and reporting
│   └── pipeline.py                 # Main orchestrator
│
├── data/
│   ├── raw/                        # Raw input CSVs (git-ignored)
│   ├── processed/                  # Cleaned output CSVs (git-ignored)
│   └── taxonomy/
│       └── taxonomy.json           # Category → subcategory → keywords
│
├── reports/
│   └── quality_report.json         # QA summary (generated at runtime)
│
└── tests/
    ├── test_cleaner.py             # 15 unit tests
    ├── test_classifier.py          # 11 unit tests
    └── test_extractor.py           # 15 unit tests
```

---

## Quickstart

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/ecommerce-classifier.git
cd ecommerce-classifier
pip install -r requirements.txt
```

### 2. Run the full pipeline

```bash
python main.py
```

This will:
- Auto-generate `data/raw/products_raw.csv` with 1200 messy records
- Run all 5 pipeline steps
- Save `data/processed/products_cleaned.csv`
- Save `data/processed/products_poor_quality.csv` (records needing manual review)
- Print a quality report to terminal
- Save `reports/quality_report.json`

### 3. Use your own data

```bash
python main.py --input path/to/your_products.csv
```

Your CSV must have these columns (others are optional):

| Column | Required | Description |
|--------|----------|-------------|
| `product_id` | Yes | Unique record ID |
| `sku` | Yes | Stock keeping unit |
| `product_name` | Yes | Raw product name string |
| `brand` | No | Brand name (can be missing/junk) |
| `category` | No | Existing category label (used as fallback) |
| `price` | No | Numeric price |
| `size` | No | Size string |
| `color` | No | Color string |
| `stock_quantity` | No | Integer stock count |
| `rating` | No | Float 1.0–5.0 |

### 4. Other CLI options

```bash
python main.py --n 5000              # Generate 5000 synthetic records
python main.py --no-generate         # Fail if raw CSV is missing
python main.py --taxonomy path/to/taxonomy.json   # Custom taxonomy
```

---

## Taxonomy

The taxonomy lives in `data/taxonomy/taxonomy.json`. It maps:

```
Category → Subcategory → [keyword list]
```

**8 top-level categories**, **35 subcategories**, **300+ keywords**.

| Category | Subcategories |
|----------|--------------|
| Electronics | Mobile Phones, Laptops, Tablets, Headphones, Cameras, Televisions, Accessories |
| Clothing | Men's, Women's, Kids', Activewear, Winter Wear, Innerwear |
| Footwear | Sports, Casual, Formal, Sandals, Boots |
| Home & Kitchen | Cookware, Appliances, Furniture, Bedding, Storage |
| Beauty & Personal Care | Skincare, Haircare, Makeup, Fragrances, Bath & Body |
| Sports & Fitness | Gym Equipment, Sports Accessories, Outdoor Sports, Yoga & Wellness |
| Books & Stationery | Books, Stationery, Art Supplies |
| Toys & Games | Educational Toys, Action Figures, Board Games |

To add a new category, edit the JSON — no code changes needed.

---

## How the classifier works

For each product, the classifier:

1. Builds a text corpus from `product_name + subcategory + brand`
2. Scores every `(category, subcategory)` pair by counting keyword hits (whole-word regex match)
3. Picks the highest-scoring pair
4. Assigns a confidence level: `high` (≥3 hits), `medium` (2), `low` (1), `none` (0)
5. Falls back to the existing category label if score is zero and it's already valid

This is intentionally simple and auditable — every classification decision is logged with its score.

---

## Output columns

The final CSV has **28 columns**:

| Column | Source | Description |
|--------|--------|-------------|
| `product_id`, `sku`, `product_name` | Raw | Original identifiers |
| `brand`, `category`, `subcategory` | Raw → cleaned | Standardized |
| `price`, `stock_quantity`, `rating` | Raw → cleaned | Coerced to correct types |
| `cleaning_notes` | Cleaner | What was fixed per record |
| `has_missing_critical` | Cleaner | True if name/SKU/price is missing |
| `classified_category` | Classifier | Taxonomy top-level category |
| `classified_subcategory` | Classifier | Taxonomy subcategory |
| `classification_confidence` | Classifier | high / medium / low / none |
| `classification_reason` | Classifier | Keyword score or fallback reason |
| `extracted_brand` | Extractor | Brand from name regex |
| `extracted_ram` | Extractor | e.g. "8GB RAM" |
| `extracted_storage` | Extractor | e.g. "256GB", "1TB" |
| `extracted_size` | Extractor | Size from name or size field |
| `extracted_color` | Extractor | Color token |
| `extracted_model` | Extractor | Model code e.g. "WH-1000XM5" |
| `name_cleaned` | Extractor | Lowercased, normalized name |
| `quality_score` | QA | 0–100 composite score |
| `quality_issues` | QA | Human-readable issue flags |
| `quality_tier` | QA | GOOD / ACCEPTABLE / POOR |

---

## Running tests

```bash
pytest tests/ -v
```

**41 unit tests** covering:
- Junk value detection and nullification
- Exact and near-duplicate removal
- Price, rating, and stock cleaning
- Color, size, and brand normalization
- Keyword-based classification for 6+ product types
- RAM vs storage disambiguation
- Volume and apparel size extraction
- Model code extraction

---

## Tech stack

- **Python 3.9+**
- **pandas** – data manipulation
- **numpy** – numeric operations
- **re** (stdlib) – regex attribute extraction
- **json** (stdlib) – taxonomy loading
- **pytest** – unit tests

No ML dependencies. The classifier is entirely rule-based and interpretable.

---

## Extending this project

**Add ML classification:** Replace `classifier.py` with a fine-tuned text classifier (e.g., `sentence-transformers` + cosine similarity against category descriptions).

**Add a REST API:** Wrap `pipeline.py` in FastAPI to expose `/classify` and `/clean` endpoints.

**Add a database sink:** Replace the CSV output in `pipeline.py` with a SQLAlchemy write to PostgreSQL.

**Connect real data:** Point `--input` at an exported CSV from Shopify, WooCommerce, or any PIM system.

---

## License

MIT
