"""draft_report.py - Part 3, Task 3.1: Context-Insight-Implication drafts."""
import json
import os
import sqlite3

import pandas as pd

from metrics_engine import (compute_percentage_change_v1,
                            flag_significant_regions_v1, MONTHS)

DRAFTS_FILE = "report_drafts.json"
LABEL = {"2026-04": "April", "2026-05": "May", "2026-06": "June"}


def load_metrics(db="pharmeasy.db"):
    """Region -> monthly sales, order counts and MoM % (all from SQL)."""
    conn = sqlite3.connect(db)
    df = pd.read_sql_query(
        "SELECT region, strftime('%Y-%m', order_date) AS month, "
        "SUM(sales_inr) AS sales, COUNT(DISTINCT order_id) AS orders "
        "FROM orders_clean GROUP BY region, month", conn)
    conn.close()
    metrics = {}
    for region, grp in df.groupby("region"):
        s = dict(zip(grp.month, grp.sales.round(2)))
        o = dict(zip(grp.month, grp.orders))
        changes = {}
        for prev, cur in zip(MONTHS[:-1], MONTHS[1:]):
            changes[f"{prev}->{cur}"] = round(
                compute_percentage_change_v1(s[cur], s[prev]), 2)
        metrics[region] = {"sales": s, "orders": o, "changes": changes}
    return metrics


def get_flagged(metrics, threshold=8):
    """Transition -> list of flagged regions."""
    flagged = {}
    for prev, cur in zip(MONTHS[:-1], MONTHS[1:]):
        key = f"{prev}->{cur}"
        ch = {r: m["changes"][key] for r, m in metrics.items()}
        flagged[key] = flag_significant_regions_v1(ch, threshold)
    return flagged


def draft_report_v1(flagged_regions, metrics):
    """One Context-Insight-Implication block per UNIQUE flagged region."""
    unique = sorted({r for regs in flagged_regions.values() for r in regs})
    blocks = []
    for region in unique:
        m = metrics[region]
        s, ch = m["sales"], m["changes"]
        hit = [k for k, regs in flagged_regions.items() if region in regs]
        names = " and ".join(" to ".join(LABEL[x] for x in k.split("->")) for k in hit)
        context = (f"{region} sales were INR {s['2026-04']:,.2f} in April, "
                   f"INR {s['2026-05']:,.2f} in May and INR {s['2026-06']:,.2f} "
                   f"in June 2026 ({sum(m['orders'].values())} orders in total).")
        insight = (f"Month-on-month change was {ch['2026-04->2026-05']:+.2f}% "
                   f"(April to May) and {ch['2026-05->2026-06']:+.2f}% "
                   f"(May to June); it crossed the 8% alert in {names}.")
        if len(hit) == 2:
            impl = ("Flagged in both transitions, so the number is volatile; "
                    "a person should review the order-level data before acting.")
        else:
            impl = ("Flagged in one transition only; worth a human look at the "
                    "order mix. The 8% rule is an alert, not a statistical test.")
        blocks.append({"region": region, "context": context,
                       "insight": insight, "implication": impl,
                       "status": "pending_review",
                       "downstream_use_allowed": False})
    return blocks


def save_drafts(blocks, path=DRAFTS_FILE):
    with open(path, "w") as f:
        json.dump(blocks, f, indent=2)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath("pharmeasy_orders_raw")))  # work from project folder
    metrics = load_metrics()
    flagged = get_flagged(metrics)
    blocks = draft_report_v1(flagged, metrics)
    print(f"{len(blocks)} CII blocks drafted for unique flagged regions:")
    for b in blocks:
        print(f"\n[{b['region']}]\n  Context    : {b['context']}\n"
              f"  Insight    : {b['insight']}\n  Implication: {b['implication']}")
    save_drafts(blocks)
    print(f"\nSaved {DRAFTS_FILE} (all drafts pending human review)")
