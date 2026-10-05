"""review_gate.py - Part 3, Task 3.4: human review gate + audit log + test harness."""
import json
import os
import uuid
from datetime import datetime, timezone

from draft_report import (DRAFTS_FILE, draft_report_v1, get_flagged,
                          load_metrics, save_drafts)

AUDIT_FILE = "audit_log.jsonl"
RUN_ID = uuid.uuid4().hex[:8]          # one id per run
ALLOWED = ("approve", "edit", "reject")


def review_gate_v1(report, decision, reviewer_note=""):
    """Validate decision, update the report, append one audit-log line."""
    if decision not in ALLOWED:
        raise ValueError(f"decision must be one of {ALLOWED}, got {decision!r}")
    updated = dict(report)
    updated["status"] = {"approve": "approved", "edit": "needs_edit",
                         "reject": "rejected"}[decision]
    updated["decision"] = decision
    updated["reviewer_note"] = reviewer_note
    updated["downstream_use_allowed"] = decision == "approve"
    entry = {"timestamp": datetime.now(timezone.utc).isoformat(),
             "run_id": RUN_ID, "region": report.get("region", "unknown"),
             "decision": decision, "reviewer_note": reviewer_note}
    with open(AUDIT_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return updated


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath("pharmeasy_orders_raw")))  # work from project folder
    metrics = load_metrics()
    blocks = draft_report_v1(get_flagged(metrics), metrics)
    by_region = {b["region"]: b for b in blocks}

    # Test harness: exercise all 3 decision paths and show before/after state
    tests = {"Guntur": ("approve", "Numbers match SQL output; memo.md covers it."),
             "Bengaluru": ("edit", "Add the May to June figure to the insight."),
             "Vijayawada": ("reject", "Only -12.02% in one transition; hold.")}
    for region, (decision, note) in tests.items():
        before = by_region[region]
        after = review_gate_v1(before, decision, note)
        by_region[region] = after
        print(f"\n{region}: BEFORE status={before['status']}, "
              f"downstream_use_allowed={before['downstream_use_allowed']}")
        print(f"{region}: AFTER  status={after['status']}, "
              f"downstream_use_allowed={after['downstream_use_allowed']}, note={note!r}")
    try:
        review_gate_v1(blocks[0], "maybe")
    except ValueError as e:
        print("\nInvalid decision rejected:", e)

    save_drafts(list(by_region.values()))
    with open(AUDIT_FILE) as f:
        print(f"\nSaved {DRAFTS_FILE}; audit_log.jsonl now has {sum(1 for _ in f)} entries")
