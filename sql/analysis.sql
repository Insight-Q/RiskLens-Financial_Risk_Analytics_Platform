-- ============================================
-- Day 2 Analysis — Person B (SQL Role)
-- Financial Risk Analytics - Loan Default
-- ============================================

-- QUERY 1: Overall Default Rate
SELECT 
    "age",
    COUNT(*) AS total_customers,
    SUM("SeriousDlqin2yrs") AS total_defaults,
    ROUND(AVG("SeriousDlqin2yrs") * 100, 2) AS default_rate_pct,
    ROUND(AVG(AVG("SeriousDlqin2yrs") * 100) OVER (), 2) AS overall_avg_default_rate
FROM loans
GROUP BY "age"
ORDER BY "age";


-- QUERY 2: Default Rate by Age Group
SELECT 
    CASE 
        WHEN "age" < 30 THEN 'Under 30'
        WHEN "age" BETWEEN 30 AND 45 THEN '30-45'
        WHEN "age" BETWEEN 46 AND 60 THEN '46-60'
        ELSE '60+'
    END AS age_group,
    COUNT(*) AS total_customers,
    SUM("SeriousDlqin2yrs") AS defaults,
    ROUND(AVG("SeriousDlqin2yrs") * 100, 2) AS default_rate_pct
FROM loans
GROUP BY age_group
ORDER BY default_rate_pct DESC;


-- QUERY 3: Income Tier vs Default Rate
SELECT 
    CASE 
        WHEN "MonthlyIncome" IS NULL THEN 'Unknown'
        WHEN "MonthlyIncome" < 2000 THEN 'Low (<2k)'
        WHEN "MonthlyIncome" BETWEEN 2000 AND 5000 THEN 'Mid (2k-5k)'
        WHEN "MonthlyIncome" BETWEEN 5001 AND 10000 THEN 'High (5k-10k)'
        ELSE 'Very High (10k+)'
    END AS income_tier,
    COUNT(*) AS total_customers,
    SUM("SeriousDlqin2yrs") AS defaults,
    ROUND(AVG("SeriousDlqin2yrs") * 100, 2) AS default_rate_pct
FROM loans
GROUP BY income_tier
ORDER BY default_rate_pct DESC;


-- QUERY 4: High Risk Customers Count
SELECT 
    COUNT(*) AS high_risk_customers
FROM loans
WHERE "SeriousDlqin2yrs" = 1
  AND "DebtRatio" > 0.5
  AND "NumberOfTimes90DaysLate" > 0;