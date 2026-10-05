# Reliability Checklist for memo.md

1. **Safety check:** I confirmed that memo.md, report_drafts.json and the dashboard use only region-level aggregates (order IDs appear only in my own checks), with no customer names, phone numbers or addresses, and no outside facts such as competitors or festivals.
2. **Validation:** I re-ran the SQL totals for Guntur (INR 62,442.27 in April, INR 138,738.93 in May, +122.19%) and matched every [HIGH] number in the memo to the queries.py output, including 51 vs 77 distinct orders.
3. **Critique and refine:** I tested the weakest claim, "a shift toward larger orders", against the data (average order value +47.16%, five largest May orders = 27.46% of sales), and so labelled the cause as a hypothesis instead of a finding and moved it to Assumptions.
4. **Human sign-off:** I reviewed the Guntur draft myself and recorded `approve` in audit_log.jsonl through review_gate_v1 in review_gate.py, which sets downstream use to allowed only for that decision.
