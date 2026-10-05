"""app.py - Part 4: PharmEasy Regional Pulse dashboard. Run: streamlit run app.py"""
import json
import os
import sqlite3
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Data logic (calculations, kept separate from the page layout below)
# ---------------------------------------------------------------------------
# Folder that holds this file (falls back to the current folder in a notebook)
BASE = (os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals()
        else os.getcwd())
if BASE not in sys.path:
    sys.path.insert(0, BASE)          # so "import metrics_engine" always finds it

from metrics_engine import compute_percentage_change_v1  # noqa: E402

DB_FILE = os.path.join(BASE, "pharmeasy.db")
THRESHOLD = 8   # same fixed alert rule as flag_significant_regions_v1


def month_label(month):
    """'2026-05' -> 'May'."""
    return pd.to_datetime(month + "-01").strftime("%B")


def load_orders(db=DB_FILE):
    conn = sqlite3.connect(db)
    df = pd.read_sql_query("SELECT * FROM orders_clean", conn)
    conn.close()
    df["month"] = df["order_date"].astype(str).str[:7]
    return df


def load_regions(db=DB_FILE):
    """All regions from regions_master (includes zero-order regions like Kurnool)."""
    conn = sqlite3.connect(db)
    regions = pd.read_sql_query("SELECT region FROM regions_master", conn)["region"]
    conn.close()
    return sorted(regions.astype(str).str.strip().tolist())


def kpis(df):
    """(total sales, total profit, distinct order count). Safe for empty data."""
    if df.empty:
        return 0.0, 0.0, 0
    # distinct order_id count, NOT a raw row count
    return (float(df["sales_inr"].sum()), float(df["profit_inr"].sum()),
            int(df["order_id"].nunique()))


def monthly_table(df, regions=None, months=None):
    """Per region and month: orders, sales, profit, MoM % and 8% flag.
    Every region/month pair is present (zero if no orders), so regions with
    no data (e.g. Kurnool) do not break anything."""
    months = months or sorted(df["month"].unique())
    regions = regions or sorted(df["region"].unique())
    base = (df.groupby(["region", "month"])
              .agg(orders=("order_id", "nunique"), sales_inr=("sales_inr", "sum"),
                   profit_inr=("profit_inr", "sum")))
    idx = pd.MultiIndex.from_product([regions, months], names=["region", "month"])
    t = base.reindex(idx, fill_value=0).reset_index()
    t["mom_pct"] = float("nan")
    for region, g in t.groupby("region"):
        prev = None
        for i, row in g.iterrows():
            if prev is not None:
                t.loc[i, "mom_pct"] = compute_percentage_change_v1(row["sales_inr"], prev)
            prev = row["sales_inr"]
    t["flagged_8pct"] = t["mom_pct"].abs() > THRESHOLD    # NaN -> False
    return t.round(2)


def _change(cur, prev):
    return compute_percentage_change_v1(cur, prev)


def exec_summary(df_scope, df_all, region):
    """Exactly 5 sentences (CII style) built only from computed numbers."""
    scope = "all regions" if region == "All" else region
    pointer = ("Use the region filter and the sections below to explore "
               "categories, charts and the monthly detail.")
    if df_scope.empty:
        return " ".join([
            f"{scope} has no orders in the data (0 distinct orders and INR 0 in sales).",
            "No monthly trend can be shown because there are no orders in any month.",
            "No category breakdown is available for the same reason.",
            f"Confirm with the regional team that {scope} is expected to be inactive "
            "before treating this as a problem.",
            pointer])

    sales, profit, orders = kpis(df_scope)
    months = sorted(df_all["month"].unique())
    s = df_scope.groupby("month")["sales_inr"].sum().reindex(months, fill_value=0.0)
    parts = [f"INR {s.iloc[0]:,.0f} in {month_label(months[0])}"]
    for prev, cur in zip(months[:-1], months[1:]):
        parts.append(f"INR {s[cur]:,.0f} in {month_label(cur)} "
                     f"({_change(s[cur], s[prev]):+.2f}%)")
    trend = "Monthly sales moved from " + " to ".join(parts[:2]) + \
            "".join(f" and {p}" for p in parts[2:]) + "."

    cat = df_scope.groupby("category")["sales_inr"].sum().sort_values(ascending=False)
    top, share = cat.index[0], cat.iloc[0] / cat.sum() * 100

    s1 = (f"From {month_label(months[0])} to {month_label(months[-1])} 2026, {scope} recorded "
          f"INR {sales:,.0f} in sales and INR {profit:,.0f} in profit from "
          f"{orders:,} distinct orders.")
    tab = monthly_table(df_all, months=months)
    if region == "All":
        big = tab.loc[tab["mom_pct"].abs().idxmax()]
        i = months.index(big["month"])
        s3 = (f"{top} is the largest category ({share:.1f}% of sales), and {big['region']} "
              f"shows the largest regional swing ({big['mom_pct']:+.2f}% from "
              f"{month_label(months[i-1])} to {month_label(months[i])}).")
        s4 = (f"Treat the {big['region']} swing as a verify-first item, not proof of a "
              f"lasting shift, and review its order mix before acting.")
    else:
        s3 = f"{top} is the largest category here ({share:.1f}% of sales)."
        fl = tab[(tab["region"] == region) & tab["flagged_8pct"]]
        if len(fl):
            names = " and ".join(month_label(m) for m in fl["month"])
            s4 = (f"{region} crossed the 8% change alert in {names}, so review its "
                  f"order mix before acting.")
        else:
            s4 = f"{region} stayed inside the 8% alert band, so routine monitoring is enough."
    return " ".join([s1, trend, s3, s4, pointer])

HIGHLIGHT = "#E4572E"   # reserved for the flagged flagship case (Guntur)
NEUTRAL = "#9AA5B1"     # all other regions
SELECTED = "#1F4E79"    # a single selected (non-flagship) region
BLUES = ["#08306B", "#2171B5", "#4292C6", "#6BAED6", "#9ECAE1", "#C6DBEF"]
DRAFTS_FILE = os.path.join(BASE, "report_drafts.json")

# ---------------------------------------------------------------------------
# Page layout
# ---------------------------------------------------------------------------
st.set_page_config(page_title="PharmEasy Regional Pulse", layout="wide")
st.title("PharmEasy Regional Pulse")
st.caption("Regional order performance, April to June 2026")

if not os.path.exists(DB_FILE):
    st.error("pharmeasy.db not found. Run `python run_pipeline.py` first, "
             "then start the dashboard again.")
    st.stop()


@st.cache_data
def get_data():
    return load_orders(), load_regions()


df_all, regions = get_data()
months = sorted(df_all["month"].unique())
region = st.selectbox("Region filter (updates every section)", ["All"] + regions)
df = df_all if region == "All" else df_all[df_all["region"] == region]
has_data = not df.empty

# ---- Executive summary (CII format, 5 sentences) ----
st.info(exec_summary(df, df_all, region))

# ---- Level 1: Overview ----
st.header("1. Overview")
sales, profit, orders = kpis(df)
c1, c2, c3 = st.columns(3)
c1.metric("Total sales (INR)", f"{sales:,.0f}")
c2.metric("Total profit (INR)", f"{profit:,.0f}")
c3.metric("Total orders (distinct order_id)", f"{orders:,}")

tab = monthly_table(df_all, regions=regions, months=months)
shown = tab if region == "All" else tab[tab["region"] == region]

# Line chart: monthly sales by region (time axis, starts at zero)
if has_data:
    fig = go.Figure()
    for r, g in shown.groupby("region"):
        if g["sales_inr"].sum() == 0:
            continue                      # skip regions with no orders
        color = HIGHLIGHT if r == "Guntur" else (NEUTRAL if region == "All" else SELECTED)
        labels = [""] * (len(g) - 1) + [r]
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(g["month"] + "-01"), y=g["sales_inr"], name=r,
            mode="lines+markers+text", text=labels, textposition="middle right",
            line=dict(color=color, width=3 if r == "Guntur" else 2),
            marker=dict(color=color)))
    fig.update_layout(
        title="How did monthly sales change from April to June 2026?",
        xaxis=dict(title="Month (2026)", tickformat="%b",
                   tickvals=list(pd.to_datetime([m + "-01" for m in months]))),
        yaxis=dict(title="Sales (INR)", rangemode="tozero"),
        showlegend=False, margin=dict(r=120))
    st.plotly_chart(fig)
else:
    st.info(f"{region} has no orders, so there is no monthly trend to chart.")

# Bar chart: total sales by region (all regions for comparison, zero included)
tot = (df_all.groupby("region")["sales_inr"].sum()
       .reindex(regions, fill_value=0.0).sort_values())
fig = go.Figure(go.Bar(
    x=tot.values, y=list(tot.index), orientation="h",
    marker_color=[HIGHLIGHT if r == "Guntur" else NEUTRAL for r in tot.index]))
fig.update_layout(
    title="Which regions bring in the most sales (April to June 2026)?",
    xaxis=dict(title="Total sales (INR)", rangemode="tozero"),
    yaxis=dict(title="Region"))
st.plotly_chart(fig)

# ---- Level 2: Category ----
st.header("2. Category")
if has_data:
    cat = df.groupby("category")["sales_inr"].sum().sort_values(ascending=False)
    fig = go.Figure(go.Pie(labels=list(cat.index), values=list(cat.values), hole=0.5,
                           marker=dict(colors=BLUES[:len(cat)]),
                           textinfo="label+percent", sort=False))
    title_scope = "all regions" if region == "All" else region
    fig.update_layout(title=f"Which categories make up sales for {title_scope}?")
    st.plotly_chart(fig)
    cat_table = (df.groupby("category")
                   .agg(orders=("order_id", "nunique"), sales_inr=("sales_inr", "sum"),
                        profit_inr=("profit_inr", "sum"))
                   .round(2).sort_values("sales_inr", ascending=False).reset_index())
    cat_table.columns = ["category", "orders", "sales (INR)", "profit (INR)"]
    st.dataframe(cat_table, hide_index=True)
else:
    st.info(f"{region} has no orders, so there is no category breakdown.")

# ---- Level 3: Detail ----
st.header("3. Detail: region by month")
detail = shown.copy()
detail["month"] = detail["month"].map(month_label)
detail = detail.rename(columns={"sales_inr": "sales (INR)", "profit_inr": "profit (INR)",
                                "mom_pct": "MoM sales change (%)",
                                "flagged_8pct": "flagged (>8%)"})
st.dataframe(detail, hide_index=True)

# ---- Reviewed CII drafts ----
st.header("Reviewed region narratives")
if os.path.exists(DRAFTS_FILE):
    with open(DRAFTS_FILE) as f:
        drafts = json.load(f)
    if region == "All":
        st.dataframe(pd.DataFrame([{"region": d["region"], "status": d["status"],
                                    "downstream use allowed": d["downstream_use_allowed"]}
                                   for d in drafts]), hide_index=True)
    else:
        d = next((x for x in drafts if x["region"] == region), None)
        if d:
            st.write(f"**Status:** {d['status']}")
            st.write(f"**Context:** {d['context']}")
            st.write(f"**Insight:** {d['insight']}")
            st.write(f"**Implication:** {d['implication']}")
        else:
            st.write("No narrative: this region was not flagged by the 8% rule.")
else:
    st.write("Run `python run_pipeline.py` first to create the narratives.")
