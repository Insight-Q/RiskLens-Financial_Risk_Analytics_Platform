-- Script 3: Income vs Default Analysis


-- step 1: create income categories
WITH income_groups AS (
    SELECT 
        "MonthlyIncome",
        "SeriousDlqin2yrs",

        CASE
            WHEN "MonthlyIncome" < 30000 THEN 'Low Income'
            WHEN "MonthlyIncome" < 70000 THEN 'Mid Income'
            ELSE 'High Income'
        END AS income_category

    FROM 
        loans
),

-- step 2: rank customers within each income group (just for exploration)
ranked AS (
    SELECT 
        income_category,
        "SeriousDlqin2yrs",
        "MonthlyIncome",

        ROW_NUMBER() OVER (
            PARTITION BY income_category 
            ORDER BY "MonthlyIncome" DESC
        ) AS rank_in_group

    FROM 
        income_groups
)

-- step 3: final aggregation
SELECT 
    income_category,
    COUNT(*) AS total_customers,

    -- calculating default rate (% of people who defaulted)
    ROUND(SUM("SeriousDlqin2yrs") * 100.0 / COUNT(*), 2) AS default_rate_pct,

    -- average income in each category
    ROUND(AVG("MonthlyIncome")::numeric, 2) AS avg_income

FROM 
    ranked
	
GROUP BY 
    income_category
	
ORDER BY 
    default_rate_pct DESC;