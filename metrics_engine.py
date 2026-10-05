"""metrics_engine.py - Task 2.4: flagging + state persistence (demo runs when executed)."""
import json
import os
import sqlite3
import pandas as pd

MONTHS = ["2026-04", "2026-05", "2026-06"]


def compute_percentage_change_v1(current, previous):
    if previous == 0:
        return 0
    return (current - previous) / previous * 100


def flag_significant_regions_v1(changes, threshold=8):
    return [r for r, pct in changes.items() if abs(pct) > threshold]


def save_state_v1(month_summary, path):
    with open(path, "w") as f:
        json.dump(month_summary, f, indent=2)


def load_previous_state_v1(path):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def monthly_sales(db="pharmeasy.db"):
    conn = sqlite3.connect(db)
    df = pd.read_sql_query(
        "SELECT region, strftime('%Y-%m', order_date) AS month, "
        "SUM(sales_inr) AS sales FROM orders_clean GROUP BY region, month",
        conn)
    conn.close()
    return df


def month_summary(df, month):
    sub = df[df.month == month]
    return {r: round(float(s), 2) for r, s in zip(sub.region, sub.sales)}


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath("pharmeasy_orders_raw")))  # work from project folder
    df = monthly_sales()
    print(df.pivot(index="region", columns="month", values="sales").round(2))

    summaries = {m: month_summary(df, m) for m in MONTHS}
    save_state_v1(summaries[MONTHS[0]], "state_2026-04.json")
    prev_apr = load_previous_state_v1("state_2026-04.json")  # reload

    transitions = [(MONTHS[0], MONTHS[1]), (MONTHS[1], MONTHS[2])]
    for prev_m, cur_m in transitions:
        prev = prev_apr if prev_m == MONTHS[0] else summaries[prev_m]
        cur = summaries[cur_m]
        changes = {r: round(compute_percentage_change_v1(cur[r], prev.get(r, 0)), 2)
                   for r in cur}
        print(f"\n{prev_m} -> {cur_m} MoM %:")
        for r, c in sorted(changes.items(), key=lambda x: -abs(x[1])):
            print(f"  {r:15s} {c:+8.2f}")
        print("Flagged:", flag_significant_regions_v1(changes, threshold=8))
