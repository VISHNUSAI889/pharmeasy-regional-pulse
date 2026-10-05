# Data-Quality Report

| Cleaning fix (Task 1.2) | Dimension | Why |
|---|---|---|
| Removed 59 exact duplicate rows | **Uniqueness** | Each order should appear once, otherwise sales and counts are inflated. |
| Stripped spaces and title-cased `region` (16 variants -> 9 names) | **Consistency** | One region must be written one way so GROUP BY and JOINs work. |
| Checked cleaned regions against `regions_master.csv` | **Validity** | Values must belong to the allowed list of regions. |
| Filled 48 missing `category` using the product -> category lookup | **Completeness** | The lookup is exact, so no rows are dropped and the value is also **Accuracy**-safe. |
| Filled 94 missing `profit_inr` with sales x category mean margin | **Completeness** | An estimate, so it trades some **Accuracy** for keeping the row. |
| `validate_schema()` checks all 8 required columns | **Validity** | Stops the pipeline early if the structure is wrong. |
| Orders limited to April-June 2026, monthly state saved as JSON | **Timeliness** | Data is current for the review month and state is reusable next month. |
| Kurnool kept in `regions_master` with zero orders | **Relevance** | The desk needs to see regions with no activity, not only regions with orders. |

All 7 dimensions: accuracy, completeness, consistency, timeliness, validity, uniqueness, relevance.
