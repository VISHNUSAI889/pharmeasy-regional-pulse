"""run_pipeline.py - runs every pipeline stage in order.

Usage:
    python run_pipeline.py               # uses existing CSV files
    python run_pipeline.py --regenerate  # rebuilds the CSV files (overwrites them)

Start the dashboard afterwards with:  streamlit run app.py
"""
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "pharmeasy_orders_raw.csv")
MASTER = os.path.join(BASE, "regions_master.csv")


def run(script, *args):
    print("=" * 20, script, "=" * 20, flush=True)
    result = subprocess.run([sys.executable, script, *args], cwd=BASE)
    if result.returncode != 0:
        sys.exit(f"\nERROR in {script}. Pipeline stopped.")


if __name__ == "__main__":
    if "--regenerate" in sys.argv:
        run("generate_dataset.py", "--force")
    elif not (os.path.exists(RAW) and os.path.exists(MASTER)):
        run("generate_dataset.py")
    else:
        print("CSV files found - skipping dataset generation.")

    for script in ["clean_data.py", "build_db.py", "queries.py",
                   "metrics_engine.py", "draft_report.py", "review_gate.py"]:
        run(script)

    print("\nAll steps finished OK. Now run: streamlit run app.py")
