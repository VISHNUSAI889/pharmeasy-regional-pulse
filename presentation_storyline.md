# Presentation Storyline: Guntur, April to May 2026

## A. For an executive (Situation - Complication - Resolution)
- **Situation:** Company sales were steady at about INR 1.07 to 1.10 million a month from April to June 2026 (+2.89% from April to May, -1.21% from May to June).
- **Complication:** Inside that steady total, Guntur's sales rose +122.19% from April to May (INR 62,442.27 to INR 138,738.93), lifting its share of company sales from 5.82% to 12.58%, and then fell 28.11% in June. We do not yet know whether this is real demand or a few large orders.
- **Resolution:** Hold any investment or target change for Guntur until the regional lead has reviewed the largest May orders, and re-check with the July export. Until then we treat the jump as a "verify first" item, not a trend.

## B. For a regional manager (Overview - Category - Detail)
- **Overview:** Guntur sales went from INR 62,442.27 to INR 138,738.93 (+122.19%), the biggest swing of all 9 active regions.
- **Category:** Wellness & Nutrition (+INR 33,787.42) and Medical Devices (+INR 23,276.06) account for about 75% of the INR 76,296.66 increase; Lab Tests added INR 11,012.02.
- **Detail:** Distinct orders rose from 51 to 77 (+50.98%) and average order value from INR 1,224.36 to INR 1,801.80 (+47.16%); the five largest May orders total INR 38,091.04 (27.46% of May). Method: cleaned data (2,100 orders) loaded to SQLite, sales summed per region and month with GROUP BY, change = (current - previous) / previous x 100, flagged when the absolute change is above 8%.

## C. Anticipated pushback

**Q1. Why should I believe this number?**
1. *Acknowledge:* It is fair to doubt a +122% swing, because the data had 59 duplicate rows and missing values that were fixed before any total was computed.
2. *Verified vs not verified:* Verified: the SQL totals, the distinct order counts (51 and 77) and the absence of duplicate order IDs. Not verified: whether each individual order is a real sale, because we only have the export.
3. *What resolves it:* The regional lead checks the five largest May orders against source records before the next monthly review.

**Q2. What if an alternative explanation is driving this?**
1. *Acknowledge:* Yes, a low April base or a few large orders could explain the jump instead of lasting demand.
2. *Verified vs not verified:* Verified: both order count and average order value rose, and the five largest orders are 27.46% of May sales. Not verified: the cause, which the order data alone cannot show (this is stated as a hypothesis in memo.md).
3. *What resolves it:* The July export. If July stays near the May level, demand rose; if it drops toward April's INR 62,442.27, the jump was order mix. Decision at the next monthly review.

**Q3. What did you not check?**
1. *Acknowledge:* I did not check anything outside the order export.
2. *Verified vs not verified:* Verified: internal consistency of the data. Not checked: customer-level repeat behaviour, discounts, stock availability, or why the orders were placed.
3. *What resolves it:* Ask the regional lead for those records for Guntur's May orders before the next monthly review.
