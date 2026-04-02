
-- Script 4: Final Combined Analysis (Export Ready)


SELECT 
    risk_category,
    income_category,

    COUNT(*) AS total_customers,

    ROUND(
        SUM("SeriousDlqin2yrs") * 100.0 / COUNT(*), 2) AS default_rate_pct

FROM (
    SELECT 
        "MonthlyIncome",
        "DebtRatio",
        "SeriousDlqin2yrs",

        -- Risk segmentation
        CASE 
            WHEN "DebtRatio" >= 0.7 THEN 'High Risk'
            WHEN "DebtRatio" >= 0.3 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END AS risk_category,

        -- Income segmentation
        CASE
            WHEN "MonthlyIncome" < 30000 THEN 'Low Income'
            WHEN "MonthlyIncome" < 70000 THEN 'Mid Income'
            ELSE 'High Income'
        END AS income_category

    FROM loans
) combined

GROUP BY 
    risk_category, 
    income_category

ORDER BY 
    default_rate_pct DESC;