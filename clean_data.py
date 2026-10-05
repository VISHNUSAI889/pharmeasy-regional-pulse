"""clean_data.py - Task 1.2 cleaning pipeline + Task 1.3 validate_schema.

Input : pharmeasy_orders_raw.csv, regions_master.csv
Output: orders_clean.csv
"""
import os
import sys

import pandas as pd

BASE = os.path.dirname(os.path.abspath("pharmeasy_orders_raw"))
RAW_FILE = os.path.join(BASE, "pharmeasy_orders_raw.csv")
MASTER_FILE = os.path.join(BASE, "regions_master.csv")
CLEAN_FILE = os.path.join(BASE, "orders_clean.csv")


REQUIRED = ["order_id", "order_date", "region", "category",
            "product", "quantity", "sales_inr", "profit_inr"]


def validate_schema(df, required_columns):
    """Task 1.3: check every required column exists."""
    missing = [c for c in required_columns if c not in df.columns]
    return {
        "status": "blocked_schema" if missing else "validated",
        "row_count": len(df),
        "missing_columns": missing,
    }


def clean_orders(raw_path=RAW_FILE, master_path=MASTER_FILE):
    df = pd.read_csv(raw_path)
    log = {"rows_raw": len(df)}

    # 1. Remove exact duplicate rows (all columns identical)
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    log["duplicates_removed"] = before - len(df)

    # 2. Normalize region: strip whitespace + title case
    df["region"] = df["region"].astype(str).str.strip().str.title()

    # Check that every region matches the master list
    master = pd.read_csv(master_path)
    if "region" not in master.columns:
        raise SystemExit("regions_master.csv must have a column named exactly 'region'")
    canonical = set(master["region"].astype(str).str.strip().str.title())
    unmatched = sorted(set(df["region"]) - canonical)
    log["unmatched_regions"] = unmatched
    if unmatched:
        print("WARNING: regions not in master:", unmatched)

    # 3. Impute missing category from a product -> category lookup
    known = df.dropna(subset=["product", "category"]).drop_duplicates(
        subset=["product", "category"]
    )
    assert known["product"].is_unique, "A product maps to more than one category"
    lookup = known.set_index("product")["category"]
    log["category_missing_before"] = int(df["category"].isna().sum())
    df["category"] = df["category"].fillna(df["product"].map(lookup))
    log["category_missing_after"] = int(df["category"].isna().sum())

    # 4. Impute missing profit_inr using category mean margin
    df["_margin"] = df["profit_inr"] / df["sales_inr"]
    cat_margin = df.groupby("category")["_margin"].mean()  # skips NaN rows
    log["profit_missing_before"] = int(df["profit_inr"].isna().sum())
    fill = (df["sales_inr"] * df["category"].map(cat_margin)).round(2)
    df["profit_inr"] = df["profit_inr"].fillna(fill)
    df = df.drop(columns="_margin")
    log["profit_missing_after"] = int(df["profit_inr"].isna().sum())

    log["rows_clean"] = len(df)
    return df, log


if __name__ == "__main__":
    clean, log = clean_orders()
    clean.to_csv(CLEAN_FILE, index=False)
    for k, v in log.items():
        print(f"{k}: {v}")
    print("Saved orders_clean.csv")

    # Task 1.3: validate the clean data, then a deliberately broken copy
    result = validate_schema(clean, REQUIRED)
    print("Clean data  :", result)
    print("Broken copy :", validate_schema(clean.drop(columns=["profit_inr"]), REQUIRED))
    if result["status"] != "validated":
        sys.exit("Schema check failed on the clean data - stopping.")
