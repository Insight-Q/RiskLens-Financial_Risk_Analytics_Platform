# 🏦 RiskLens — Financial Risk Analytics Platform

> **End-to-end loan default prediction system** built on 150,000 real-world credit records.  
> Combines machine learning, explainable AI, interactive dashboards, and REST API — production-ready architecture.

---

## 🚀 Live Demo

| Component | Link |
|---|---|
| 📊 Streamlit Dashboard | *Coming soon* |
| ⚡ Flask REST API | *Coming soon* |

---

## 📌 Project Overview

RiskLens is a full-stack financial risk analytics platform that predicts the probability of a customer defaulting on a loan. The system ingests raw credit data, performs deep exploratory analysis, trains an optimized machine learning model, and serves predictions through both an interactive dashboard and a REST API.

The project mirrors how a real bank's risk analytics team would approach credit risk modeling — from raw data to business-ready insights.

---

## 🎯 Key Results

| Metric | Value |
|---|---|
| 🏆 Best Model | Random Forest Classifier |
| 📈 ROC-AUC Score | **0.87+** |
| 📊 Dataset Size | 150,000 customers |
| 🔍 Features Used | 11 financial features |
| ⚖️ Class Imbalance Fix | SMOTE applied |
| 💡 Explainability | SHAP values |

---

## 🔍 Key Findings

- **Late payment history** is the strongest predictor of loan default — stronger than income or debt ratio alone
- **Low income customers** (below $3,000/month) show significantly higher default rates across all age groups
- **Younger borrowers (18–30)** carry the highest risk due to lower financial stability and limited credit history
- Dataset is heavily imbalanced — **93% non-default vs 7% default** — handled using SMOTE before model training
- **Debt ratio above 0.6** is a strong warning signal — customers in this range are far more likely to default

---

## 🛠️ Tech Stack

### Data & Machine Learning
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

### Database & API
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)

### Visualization & Dashboard
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

### Explainability
![SHAP](https://img.shields.io/badge/SHAP-Explainable_AI-blueviolet?style=for-the-badge)

---

## 📁 Project Structure

```
RiskLens-Financial_Risk_Analytics_Platform/
│
├── 📂 data/
│   ├── cs-training.csv                  ← Raw dataset (150k rows)
│   └── cs-training-clean.csv            ← Cleaned + feature engineered
│
├── 📂 notebooks/
│   ├── 01_EDA_analysis.ipynb            ← Data cleaning, EDA, 6 charts
│   ├── 02_model_training.ipynb          ← ML models, SMOTE, SHAP
│   └── 03_business_insights.ipynb       ← Risk scoring, recommendations
│
├── 📂 sql/
│   ├── load_data.py                     ← CSV → PostgreSQL loader
│   └── 02_analysis.sql                  ← Advanced SQL queries
│
├── 📂 dashboard/
│   └── app.py                           ← Streamlit interactive dashboard
│
├── 📂 models/
│   └── best_model.pkl                   ← Trained Random Forest model
│
├── 📂 api/                              ← Flask REST API
│   └── app.py                           ← /predict, /health endpoints
│
├── requirements.txt
└── README.md
```

---

## ⚡ API Reference

### `POST /predict`
Predicts loan default risk for a single customer.

**Request Body:**
```json
{
  "age": 35,
  "MonthlyIncome": 5000,
  "DebtRatio": 0.4,
  "RevolvingUtilizationOfUnsecuredLines": 0.3,
  "NumberOfOpenCreditLinesAndLoans": 4,
  "NumberOfTimes90DaysLate": 0,
  "NumberOfTime30-59DaysPastDueNotWorse": 1,
  "NumberOfTime60-89DaysPastDueNotWorse": 0,
  "NumberRealEstateLoansOrLines": 1,
  "NumberOfDependents": 2
}
```

**Response:**
```json
{
  "risk_score": 42.5,
  "risk_label": "Medium Risk",
  "default_probability": 0.425
}
```

### `GET /health`
Returns API status.

### `GET /model-info`
Returns model name, features used, and performance metrics.

---

## 🗄️ SQL Analysis

Advanced PostgreSQL queries built on the 150k row dataset:

```sql
-- Default rate by age group using CASE WHEN + GROUP BY
SELECT
    CASE
        WHEN age BETWEEN 18 AND 30 THEN 'Young (18-30)'
        WHEN age BETWEEN 31 AND 45 THEN 'Middle (31-45)'
        WHEN age BETWEEN 46 AND 60 THEN 'Senior (46-60)'
        ELSE 'Old (60+)'
    END AS age_group,
    COUNT(*) AS total_customers,
    ROUND(AVG("SeriousDlqin2yrs") * 100, 2) AS default_rate_pct
FROM loans
GROUP BY age_group
ORDER BY default_rate_pct DESC;
```

Full SQL scripts available in `/sql/` folder.

---

## 📊 EDA Highlights

6 analytical charts covering:

- 📊 Default rate by age group
- 💰 Monthly income distribution
- 📉 Debt ratio boxplot — default vs non-default
- 🔥 Feature correlation heatmap
- ⚖️ Target class distribution
- 📈 Default rate by income tier

---

## 🧠 Model Pipeline

```
Raw Data (150k rows)
    ↓
Data Cleaning (missing values, outliers)
    ↓
Feature Engineering (age_group, income_tier, debt_tier)
    ↓
Train/Test Split (80/20, stratified)
    ↓
SMOTE (class imbalance fix)
    ↓
Model Training (Logistic Regression vs Random Forest)
    ↓
Evaluation (ROC-AUC, F1, Confusion Matrix)
    ↓
SHAP Explainability
    ↓
Model Saved → best_model.pkl
```

---

## 💼 Business Recommendations

Derived from model insights and EDA findings:

1. **Flag high risk customers early** — risk score above 60 should trigger manual review before loan approval
2. **Income verification** — customers earning below $3,000/month require stricter checks
3. **Late payment alerts** — 2+ late payments should trigger automated risk review
4. **Age-based credit limits** — younger borrowers (18–30) should receive smaller initial credit limits
5. **Debt ratio threshold** — customers with debt ratio above 0.6 should face stricter loan criteria

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/Insight-Q/RiskLens-Financial_Risk_Analytics_Platform.git
cd RiskLens-Financial_Risk_Analytics_Platform
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Streamlit Dashboard
```bash
cd dashboard
streamlit run app.py
```

### 4. Run Flask API
```bash
cd api
python app.py
```

### 5. Setup PostgreSQL
```bash
cd sql
python load_data.py
```

---

## 📦 Requirements

```
pandas
numpy
matplotlib
seaborn
scikit-learn
imbalanced-learn
shap
streamlit
plotly
flask
flask-cors
sqlalchemy
psycopg2-binary
joblib
```

---

## 📂 Dataset

**Give Me Some Credit** — Kaggle Competition Dataset  
🔗 [https://www.kaggle.com/c/GiveMeSomeCredit](https://www.kaggle.com/c/GiveMeSomeCredit)

- 150,000 customer records
- 11 financial features
- Binary classification target — loan default prediction

---

*Built as a portfolio project demonstrating end-to-end data analytics and machine learning engineering.*