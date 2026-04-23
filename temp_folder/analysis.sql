-- ============================================
-- File: queries.sql
-- Project: RiskLens-Financial_Risk_Analytics_Platform
-- Description: Basic database inspection and data exploration queries
-- ============================================


-- 1. Retrieve all available databases in PostgreSQL
SELECT 
	datname 
FROM 
	pg_database;

-- 2. Check the currently connected database
SELECT 
	CURRENT_DATABASE();

-- 3. Total number of customers in the loans table
SELECT
	COUNT(*) AS Total_custmors
FROM 
	loans;

-- 4. Preview first 10 records from the loans table
SELECT
	*
FROM 
	loans
LIMIT 10;

-- Query 1: Overall Default Rate
SELECT
	AVG(("SeriousDlqin2yrs")*100) AS default_rate
FROM
	loans;
-- =========================================
-- Query 2: Default Rate by Age Group
-- =========================================

SELECT
	CASE
		WHEN age < 30 THEN 'Young'
		WHEN age BETWEEN 30 AND 50 THEN 'Middle'
		ELSE 'Senior'
		END AS age_group,
		
		COUNT(*) AS Total_people,
		
		AVG(("SeriousDlqin2yrs")*100) AS default_rate
FROM
	loans

GROUP BY
	age_group

ORDER BY
	default_rate DESC;

-- Query 3: Income Tire Analysis

SELECT
	case
		WHEN "MonthlyIncome" < 3000 THEN 'Low Income'
		WHEN "MonthlyIncome" BETWEEN 3000 AND 7000 THEN 'Medium Income'
		ELSE 'High Income'
		END AS income_tire,
		
		COUNT(*) AS total_people,
		
		AVG("SeriousDlqin2yrs") AS default_rate
FROM
	loans

GROUP BY 
	income_tire

ORDER BY
	default_rate;


-- Query 4: High Risk Customers
SELECT 
	COUNT(*) AS high_risk_custmers
FROM 
	loans
WHERE 
	"SeriousDlqin2yrs" = 1
	AND "DebtRatio" > 0.5;


WITH default_customers AS (
	SELECT 
		age,
		"MonthlyIncome",
		COUNT(*) AS total_people
	FROM
		loans
	WHERE 
		"SeriousDlqin2yrs" = 1
	GROUP BY
		age,
		"MonthlyIncome"
)
SELECT
	*
FROM
	default_customers
LIMIT 10;


WITH risk_segments AS (
	SELECT 
		"MonthlyIncome",
		"DebtRatio",
		"SeriousDlqin2yrs",
		-- Risk category based on Debtratio
		CASE
			WHEN "DebtRatio" >= 0.7 THEN 'High Risk'
			WHEN "DebtRatio" >=0.3 THEN 'Medium Risk'
			ELSE 'Low Risk'
		END AS risk_category

		FROM 
			loans
)

SELECT
	risk_category,
	COUNT(*) AS total_customers,

	ROUND(AVG("MonthlyIncome")::NUMERIC,2) AS avg_income,
	ROUND(AVG("DebtRatio")::NUMERIC,2) AS avg_debtratio,
	SUM("SeriousDlqin2yrs") AS total_defaulter,
	ROUND(SUM("SeriousDlqin2yrs")*100/COUNT(*),2) AS default_rate

FROM
	risk_segments
GROUP BY 
	risk_category
ORDER BY 
	default_rate DESC;



















