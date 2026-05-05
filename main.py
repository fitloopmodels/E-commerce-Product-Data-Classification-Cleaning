"""
main.py
-------
Entry point for the E-commerce Product Classification pipeline.

Run:
  python main.py                      # default: generate + process 1200 records
  python main.py --input my_file.csv  # use your own CSV
  python main.py --n 5000             # generate 5000 records
  python main.py --no-generate        # fail if raw CSV not found
"""

import argparse
import sys
from src.pipeline import Pipeline


def parse_args():
    parser = argparse.ArgumentParser(
        description="E-commerce Product Data Classification & Cleaning Pipeline"
    )
    parser.add_argument(
        "--input", type=str, default="data/raw/products_raw.csv",
        help="Path to raw CSV input file (default: data/raw/products_raw.csv)"
    )
    parser.add_argument(
        "--taxonomy", type=str, default="data/taxonomy/taxonomy.json",
        help="Path to taxonomy JSON file"
    )
    parser.add_argument(
        "--n", type=int, default=1200,
        help="Number of synthetic records to generate if raw file is missing (default: 1200)"
    )
    parser.add_argument(
        "--no-generate", action="store_true",
        help="Do not auto-generate data; raise error if raw file is missing"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    pipeline = Pipeline(
        raw_path=args.input,
        taxonomy_path=args.taxonomy,
        generate_if_missing=not args.no_generate,
        n_records=args.n,
    )

    try:
        df = pipeline.run()
        print(f"Success. Final dataset shape: {df.shape}")
        return 0
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    sys.exit(main())
