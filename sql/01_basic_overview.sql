-- Script 1: Basic Overview of data 


SELECT 
    COUNT(*) AS total_customers
FROM 
    loans;


-- 2. looking at default vs non-default cases
-- (0 = no default, 1 = default)
SELECT 
    "SeriousDlqin2yrs" AS loan_status,
    COUNT(*) AS total_count,

    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage

FROM 
    loans

GROUP BY 
    "SeriousDlqin2yrs";


--3. income stats using MonthlyIncome
-- helps to understand earning range of customers
SELECT 
    ROUND(AVG("MonthlyIncome")::numeric, 2) AS avg_income,
    ROUND(MIN("MonthlyIncome")::numeric, 2) AS min_income,
    ROUND(MAX("MonthlyIncome")::numeric, 2) AS max_income

FROM 
    loans
	
WHERE 
    "MonthlyIncome" IS NOT NULL;