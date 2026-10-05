"""generate_dataset.py - synthetic PharmEasy order export (stand-in generator).

Creates:
  pharmeasy_orders_raw.csv  (2159 rows: 2100 unique orders + 59 exact duplicates)
  regions_master.csv        (10 regions: 9 active + Kurnool with zero orders)

Design (matches what the rest of the pipeline expects):
  * 8 columns: order_id, order_date, region, category, product, quantity,
    sales_inr, profit_inr
  * April-June 2026; each order = quantity (1-5) x unit price, profit = sales x margin
  * Region/month/category order counts and sales totals follow the TARGETS table
    below, so the project scenario (Guntur spike, Nellore stable, Kurnool empty)
    is reproduced every time. The random seed is fixed, so the output is repeatable.
  * Raw-data problems added on purpose: 16 messy region spellings, 59 exact
    duplicate rows, 48 missing categories, 96 missing profit values
    (94 after de-duplication).

If your course supplies its own generate_dataset.py, use that one instead.
Safety: existing CSV files are NOT overwritten unless you pass --force.
"""
import csv
import os
import random
import sys

SEED = 42
BASE = os.path.dirname(os.path.abspath("pharmeasy_orders_raw"))
RAW_FILE = os.path.join(BASE, "pharmeasy_orders_raw.csv")
MASTER_FILE = os.path.join(BASE, "regions_master.csv")

CATEGORIES = ["Lab Tests", "Medical Devices", "OTC Medicines",
              "Personal Care", "Prescription Medicines", "Wellness & Nutrition"]

PRODUCTS = {
    "Lab Tests": ["Full Body Checkup", "HbA1c Test", "Lipid Profile",
                  "Thyroid Profile", "Vitamin D Test"],
    "Medical Devices": ["Digital BP Monitor", "Glucometer Kit", "Nebulizer",
                        "Pulse Oximeter", "Thermometer"],
    "OTC Medicines": ["Antacid Tablets", "Cetirizine 10mg", "Cough Syrup 100ml",
                      "ORS Sachet", "Paracetamol 500mg"],
    "Personal Care": ["Antiseptic Liquid", "Baby Diaper Pack", "Face Wash",
                      "Hand Sanitizer 500ml", "Sunscreen SPF50"],
    "Prescription Medicines": ["Amlodipine 5mg", "Atorvastatin 10mg",
                               "Azithromycin 500mg", "Insulin Pen", "Metformin 500mg"],
    "Wellness & Nutrition": ["Calcium + D3 Tablets", "Fish Oil Capsules",
                             "Immunity Booster Syrup", "Multivitamin Tablets",
                             "Whey Protein 1kg"],
}
PRICE_RANGE = {"Lab Tests": (400, 1800), "Medical Devices": (350, 3200),
               "OTC Medicines": (40, 220), "Personal Care": (80, 550),
               "Prescription Medicines": (90, 650), "Wellness & Nutrition": (255, 1400)}

REGIONS = [("Hyderabad", "Telangana"), ("Warangal", "Telangana"),
           ("Karimnagar", "Telangana"), ("Visakhapatnam", "Andhra Pradesh"),
           ("Vijayawada", "Andhra Pradesh"), ("Guntur", "Andhra Pradesh"),
           ("Tirupati", "Andhra Pradesh"), ("Nellore", "Andhra Pradesh"),
           ("Bengaluru", "Karnataka"), ("Kurnool", "Andhra Pradesh")]

# Messy spellings (3 + 3 + 4 variants + 6 clean regions = 16 raw variants)
VARIANTS = {
    "Hyderabad": ["Hyderabad", " hyderabad", "HYDERABAD "],
    "Bengaluru": ["Bengaluru", " BENGALURU", "bengaluru "],
    "Vijayawada": ["Vijayawada", " Vijayawada ", "VIJAYAWADA", "vijayawada"],
}

N_DUPLICATES, N_MISSING_CATEGORY, N_MISSING_PROFIT = 59, 48, 94

# TARGETS[region][month] = [[orders, sales_inr], ...] in CATEGORIES order
TARGETS = {
    "Bengaluru": {
        "2026-04": [[7, 21586.0], [14, 76433.41], [33, 13643.75], [19, 13968.23], [29, 36750.87], [11, 41123.22]],
        "2026-05": [[4, 5283.93], [13, 63832.68], [40, 12451.49], [18, 19111.39], [22, 23895.75], [21, 48354.44]],
        "2026-06": [[3, 12257.38], [11, 63297.37], [31, 13070.68], [15, 11397.49], [19, 19830.01], [22, 50441.18]],
    },
    "Guntur": {
        "2026-04": [[3, 12578.92], [3, 9490.63], [18, 6170.02], [7, 5383.35], [12, 9521.76], [8, 19297.59]],
        "2026-05": [[6, 23590.94], [8, 32766.69], [23, 8226.44], [11, 9320.26], [14, 11749.59], [15, 53085.01]],
        "2026-06": [[6, 21126.69], [6, 30211.77], [15, 5094.17], [9, 7494.54], [14, 11518.9], [12, 24299.11]],
    },
    "Hyderabad": {
        "2026-04": [[8, 27789.75], [6, 36533.47], [51, 18739.07], [21, 24789.33], [40, 36798.05], [32, 65020.48]],
        "2026-05": [[7, 29402.39], [19, 97017.25], [44, 16932.4], [17, 14485.27], [33, 30596.03], [25, 55391.94]],
        "2026-06": [[14, 31706.57], [19, 82504.09], [64, 21959.2], [26, 23548.66], [63, 70809.01], [30, 63561.03]],
    },
    "Karimnagar": {
        "2026-04": [[0, 0.0], [7, 29194.05], [8, 3702.64], [2, 1202.41], [11, 11889.65], [1, 3826.96]],
        "2026-05": [[3, 5849.9], [6, 22665.66], [11, 5535.1], [4, 2490.57], [8, 8759.76], [6, 16284.91]],
        "2026-06": [[0, 0.0], [4, 11400.45], [5, 2888.17], [5, 3819.31], [4, 5221.35], [4, 11161.3]],
    },
    "Nellore": {
        "2026-04": [[3, 14494.8], [1, 11430.96], [13, 5863.95], [6, 5360.63], [18, 15398.16], [13, 33074.69]],
        "2026-05": [[3, 12162.34], [6, 17905.75], [14, 3213.25], [9, 6601.84], [21, 22119.09], [11, 29182.59]],
        "2026-06": [[5, 24573.62], [5, 42672.26], [17, 6558.66], [3, 1917.32], [9, 7694.01], [7, 10977.75]],
    },
    "Tirupati": {
        "2026-04": [[3, 5098.1], [4, 15107.76], [7, 2740.32], [10, 8129.95], [14, 11264.6], [5, 12242.01]],
        "2026-05": [[3, 13301.49], [8, 38506.47], [16, 5098.66], [9, 9629.77], [16, 14746.47], [6, 9800.34]],
        "2026-06": [[3, 8521.51], [6, 28008.65], [17, 6453.86], [3, 2145.55], [9, 9693.45], [12, 20707.97]],
    },
    "Vijayawada": {
        "2026-04": [[6, 23798.46], [12, 53528.02], [20, 6359.97], [18, 21627.6], [26, 33544.11], [15, 32476.03]],
        "2026-05": [[10, 28962.7], [11, 68965.87], [25, 10487.13], [13, 15358.77], [21, 22816.21], [12, 28272.89]],
        "2026-06": [[7, 22309.36], [11, 52126.23], [27, 8746.46], [18, 13827.63], [18, 21843.96], [14, 34996.04]],
    },
    "Visakhapatnam": {
        "2026-04": [[5, 11600.49], [8, 45981.4], [28, 9731.1], [8, 7053.13], [27, 32388.22], [15, 28010.95]],
        "2026-05": [[0, 0.0], [4, 23998.57], [12, 3674.41], [3, 1561.22], [8, 7540.86], [6, 13815.02]],
        "2026-06": [[1, 5819.4], [6, 22231.1], [14, 5100.2], [6, 10422.81], [7, 6842.04], [18, 50320.02]],
    },
    "Warangal": {
        "2026-04": [[2, 12405.1], [10, 39772.08], [19, 6527.23], [5, 3390.85], [18, 17361.77], [10, 21011.11]],
        "2026-05": [[5, 11176.83], [2, 3442.8], [16, 5758.07], [22, 20692.58], [19, 16730.38], [11, 20538.57]],
        "2026-06": [[1, 2289.96], [5, 17701.8], [24, 8625.24], [9, 13005.61], [9, 8112.12], [8, 16980.51]],
    },
}


def build_orders(rng):
    rows = []
    for region, months in TARGETS.items():
        for month, cells in months.items():
            for cat, (n, total) in zip(CATEGORIES, cells):
                if n == 0:
                    continue
                lo, hi = PRICE_RANGE[cat]
                items = []
                for _ in range(n):
                    qty = rng.randint(1, 5)
                    items.append((qty, qty * rng.uniform(lo, hi),
                                  rng.choice(PRODUCTS[cat])))
                scale = total / sum(w for _, w, _ in items)
                sales = [round(w * scale, 2) for _, w, _ in items]
                sales[-1] = round(total - sum(sales[:-1]), 2)   # exact cell total
                for (qty, _, prod), s in zip(items, sales):
                    day = rng.randint(1, 28)
                    margin = max(0.02, rng.gauss(0.15, 0.04))
                    rows.append({
                        "order_id": "", "order_date": f"{month}-{day:02d}",
                        "region": region, "category": cat, "product": prod,
                        "quantity": qty, "sales_inr": s,
                        "profit_inr": round(s * margin, 2)})
    rng.shuffle(rows)
    for i, r in enumerate(rows, 1):
        r["order_id"] = f"PE{i:05d}"
    return rows


def add_problems(rows, rng):
    # messy region spellings (every variant appears at least once)
    for region, options in VARIANTS.items():
        idx = [i for i, r in enumerate(rows) if r["region"] == region]
        rng.shuffle(idx)
        for k, i in enumerate(idx):
            rows[i]["region"] = options[k] if k < len(options) else rng.choice(options)
    # missing category / profit on distinct rows
    order = list(range(len(rows)))
    rng.shuffle(order)
    miss_cat = set(order[:N_MISSING_CATEGORY])
    miss_profit = [i for i in order[N_MISSING_CATEGORY:]][:N_MISSING_PROFIT]
    for i in miss_cat:
        rows[i]["category"] = ""
    for i in miss_profit:
        rows[i]["profit_inr"] = ""
    # 59 exact duplicates: none with missing category, 2 with missing profit
    ok = [i for i in range(len(rows)) if i not in miss_cat]
    with_gap = [i for i in ok if i in set(miss_profit)]
    no_gap = [i for i in ok if i not in set(miss_profit)]
    dup_idx = rng.sample(with_gap, 2) + rng.sample(no_gap, N_DUPLICATES - 2)
    out = list(rows)
    for i in dup_idx:
        out.insert(rng.randint(0, len(out)), dict(rows[i]))
    return out


def main(force=False):
    exists = [f for f in (RAW_FILE, MASTER_FILE) if os.path.exists(f)]
    if exists and not force:
        sys.exit("Files already exist: " + ", ".join(os.path.basename(f) for f in exists)
                 + ". Nothing overwritten. Use --force to regenerate.")
    rng = random.Random(SEED)
    rows = add_problems(build_orders(rng), rng)
    cols = ["order_id", "order_date", "region", "category", "product",
            "quantity", "sales_inr", "profit_inr"]
    with open(RAW_FILE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    with open(MASTER_FILE, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["region", "state"])
        w.writerows(REGIONS)
    print(f"Wrote {len(rows)} rows to {os.path.basename(RAW_FILE)} and "
          f"{len(REGIONS)} regions to {os.path.basename(MASTER_FILE)}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
