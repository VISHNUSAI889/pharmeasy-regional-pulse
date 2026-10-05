"""Task 2.1 - Load clean data into SQLite (pharmeasy.db)."""
import os
import sqlite3

import pandas as pd

BASE = os.path.dirname(os.path.abspath("pharmeasy_orders_raw"))
master = pd.read_csv(os.path.join(BASE, "regions_master.csv"))
if "region" not in master.columns:
    raise SystemExit("regions_master.csv must have a column named exactly 'region'")
orders = pd.read_csv(os.path.join(BASE, "orders_clean.csv"))

conn = sqlite3.connect(os.path.join(BASE, "pharmeasy.db"))
master.to_sql("regions_master", conn, if_exists="replace", index=False)
orders.to_sql("orders_clean", conn, if_exists="replace", index=False)
for t in ("regions_master", "orders_clean"):
    n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"{t}: {n} rows")
conn.close()
