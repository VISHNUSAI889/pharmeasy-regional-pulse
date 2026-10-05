"""queries.py - Task 2.2 JOIN validation + Task 2.3 region x month metrics (SQL)."""
import os
import sqlite3

import pandas as pd

os.chdir(os.path.dirname(os.path.abspath("pharmeasy_orders_raw")))  # work from project folder

from metrics_engine import compute_percentage_change_v1, MONTHS  # noqa: E402

conn = sqlite3.connect("pharmeasy.db")
q = lambda sql: pd.read_sql_query(sql, conn)

print("1) Row counts")
print("LEFT JOIN :", conn.execute(
    "SELECT COUNT(*) FROM regions_master r LEFT JOIN orders_clean o "
    "ON r.region = o.region").fetchone()[0])
print("INNER JOIN:", conn.execute(
    "SELECT COUNT(*) FROM regions_master r INNER JOIN orders_clean o "
    "ON r.region = o.region").fetchone()[0])

print("\n2) Duplicate order_id (expect 0 rows)")
print(q("SELECT order_id, COUNT(*) AS c FROM orders_clean "
        "GROUP BY order_id HAVING COUNT(*) > 1"))

print("\n3) COUNT(*) vs COUNT(order_id) per region")
cmp_df = q("SELECT r.region, COUNT(*) AS count_star, "
           "COUNT(o.order_id) AS count_order_id "
           "FROM regions_master r LEFT JOIN orders_clean o "
           "ON r.region = o.region GROUP BY r.region")
print(cmp_df)
print("Where they disagree:")
print(cmp_df[cmp_df.count_star != cmp_df.count_order_id])

print("\n4) Orders per region (ascending)")
print(q("SELECT r.region, COUNT(o.order_id) AS orders "
        "FROM regions_master r LEFT JOIN orders_clean o "
        "ON r.region = o.region GROUP BY r.region ORDER BY orders ASC"))

print("\n5) Total sales per region per month (SQL GROUP BY)")
sales = q("SELECT region, strftime('%Y-%m', order_date) AS month, "
          "ROUND(SUM(sales_inr), 2) AS sales_inr FROM orders_clean "
          "GROUP BY region, month ORDER BY region, month")
pivot = sales.pivot(index="region", columns="month", values="sales_inr")
print(pivot)

print("\n6) Month-on-month growth % = (current - previous) / previous x 100")
mom = pd.DataFrame(index=pivot.index)
for prev, cur in zip(MONTHS[:-1], MONTHS[1:]):
    mom[f"{prev} -> {cur}"] = [round(compute_percentage_change_v1(pivot.loc[r, cur], pivot.loc[r, prev]), 2)
                                for r in pivot.index]
print(mom)
conn.close()
