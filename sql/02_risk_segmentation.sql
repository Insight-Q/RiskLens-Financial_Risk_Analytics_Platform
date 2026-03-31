-- Script 2: Risk Segmentation


WITH risk_segments AS (
    SELECT 
        "MonthlyIncome",
        "DebtRatio",
        "SeriousDlqin2yrs",

        CASE
            WHEN "DebtRatio" >= 0.7 THEN 'High Risk'
            WHEN "DebtRatio" >= 0.3 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END AS risk_category

    FROM loans
)

SELECT 
    risk_category,
    COUNT(*) AS total_customers,

    ROUND(AVG("MonthlyIncome")::numeric, 2) AS avg_income,
    ROUND(AVG("DebtRatio")::numeric, 2) AS avg_debt_ratio,
    SUM("SeriousDlqin2yrs") AS total_defaults,

    ROUND(SUM("SeriousDlqin2yrs") * 100.0 / COUNT(*), 2) AS default_rate_pct

FROM risk_segments

GROUP BY risk_category

ORDER BY default_rate_pct DESC;