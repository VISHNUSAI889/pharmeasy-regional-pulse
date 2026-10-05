# Memo: Guntur sales, April to May 2026

Risk tags: [LOW] structural or logical, [MEDIUM] reasoned inference, [HIGH] specific number traceable to the Part 2 SQL output.

## Title
Guntur's +122.19% April-to-May sales swing: verify the order mix before acting

## Context
- Guntur sales rose from INR 62,442.27 in April to INR 138,738.93 in May 2026, a change of +122.19%. [HIGH]
- This is the largest swing of the 9 active regions in either transition (the next largest is Visakhapatnam at +99.12% from May to June). [HIGH]
- Company-wide sales barely moved over the same months: INR 1,072,207.16 to INR 1,103,140.73 (+2.89%). [HIGH]
- Guntur's share of company sales went from 5.82% in April to 12.58% in May. [HIGH]

## Key Insight
- Both the number of orders and the value per order rose in Guntur, so the jump is not explained by only one of them. [MEDIUM]
- About three quarters of the increase came from two categories, Wellness & Nutrition and Medical Devices. [HIGH]
- The jump is partly a re-allocation inside the company, because total company sales were almost flat. [MEDIUM]

## Evidence
- Distinct orders rose from 51 to 77 (+50.98%). [HIGH]
- Average order value rose from INR 1,224.36 to INR 1,801.80 (+47.16%). [HIGH]
- The total increase was INR 76,296.66; Wellness & Nutrition added INR 33,787.42 (44.28%), Medical Devices INR 23,276.06 (30.51%) and Lab Tests INR 11,012.02. [HIGH]
- The five largest May orders add up to INR 38,091.04, which is 27.46% of Guntur's May sales. [HIGH]
- In June, Guntur fell to INR 99,745.18 (-28.11% from May) but stayed 59.74% above April. [HIGH]
- The 8% rule is a fixed alert, not a statistical test, so crossing it only means a person should look. [LOW]

## Recommendation
- Do not change staffing, stock or targets for Guntur on the strength of this number alone. [MEDIUM]
- Have the regional lead review the five largest May orders and the Wellness & Nutrition and Medical Devices orders first. [MEDIUM]
- Treat the June fall to INR 99,745.18 as a sign that the May level did not hold, while the level is still above April. [MEDIUM]

## Next Check
- When the July export arrives, load the saved state and compare Guntur's July sales with June (INR 99,745.18) and May (INR 138,738.93). [LOW]
- Check whether the share of high-value orders (the five largest May orders) in the next month looks like May or like April. [MEDIUM]

## Assumptions
- Hypothesis, not verified: Guntur's +122.19% reflects a low April base and/or a shift toward larger, higher-value orders rather than a lasting rise in demand; the order data alone cannot separate these. [MEDIUM]
- The sales figures are taken as correctly recorded; the 94 imputed profit values and 48 imputed categories do not change any sales number used here, but the category split uses the imputed categories. [MEDIUM]
- With about 50 to 80 orders a month in Guntur, a few large orders can move the monthly total a lot. [MEDIUM]
