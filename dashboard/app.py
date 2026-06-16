import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import warnings
warnings.filterwarnings('ignore')

# ── Page Config ───────────────────────────────────
st.set_page_config(
    page_title="RiskLens — Financial Risk Analytics",
    page_icon="📊",
    layout="wide"
)

# ── API URL ───────────────────────────────────────
API_URL = "http://localhost:5000"

# ── Load Data ─────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('../data/cs-training-clean.csv')
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────
st.sidebar.title("🔍 Filters")

age_range = st.sidebar.slider(
    "Age Range",
    min_value=int(df['age'].min()),
    max_value=int(df['age'].max()),
    value=(25, 60)
)

income_options = ['All'] + list(df['income_tier'].dropna().unique())
selected_income = st.sidebar.selectbox("Income Tier", income_options)

# ── Filter Data ───────────────────────────────────
filtered_df = df[
    (df['age'] >= age_range[0]) &
    (df['age'] <= age_range[1])
]
if selected_income != 'All':
    filtered_df = filtered_df[
        filtered_df['income_tier'] == selected_income
    ]

# ── Title ─────────────────────────────────────────
st.title("📊 RiskLens — Financial Risk Analytics")
st.markdown("**Loan Default Prediction & Customer Risk Analysis**")
st.divider()

# ── KPI Cards ─────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 Total Customers", f"{len(filtered_df):,}")
with col2:
    default_rate = filtered_df['SeriousDlqin2yrs'].mean() * 100
    st.metric("⚠️ Default Rate", f"{default_rate:.1f}%")
with col3:
    avg_income = filtered_df['MonthlyIncome'].mean()
    st.metric("💰 Avg Monthly Income", f"${avg_income:,.0f}")
with col4:
    avg_debt = filtered_df['DebtRatio'].mean()
    st.metric("📉 Avg Debt Ratio", f"{avg_debt:.2f}")

st.divider()

# ── Charts ────────────────────────────────────────
st.subheader("📈 Customer Analysis")

col1, col2 = st.columns(2)

with col1:
    default_by_age = filtered_df.groupby(
        'age_group', observed=True
    )['SeriousDlqin2yrs'].mean() * 100

    fig1 = px.bar(
        x=default_by_age.index,
        y=default_by_age.values,
        title="Default Rate by Age Group",
        labels={'x': 'Age Group', 'y': 'Default Rate (%)'},
        color=default_by_age.values,
        color_continuous_scale='RdYlGn_r'
    )
    fig1.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    income_data = filtered_df[filtered_df['MonthlyIncome'] < 50000]
    fig2 = px.histogram(
        income_data, x='MonthlyIncome', nbins=50,
        title="Monthly Income Distribution",
        color_discrete_sequence=['#1D9E75']
    )
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    fig3 = px.box(
        filtered_df, x='SeriousDlqin2yrs', y='DebtRatio',
        title="Debt Ratio — Default vs No Default",
        color='SeriousDlqin2yrs',
        color_discrete_map={0: '#1D9E75', 1: '#E24B4A'}
    )
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    default_by_income = filtered_df.groupby(
        'income_tier', observed=True
    )['SeriousDlqin2yrs'].mean() * 100

    fig4 = px.bar(
        x=default_by_income.index,
        y=default_by_income.values,
        title="Default Rate by Income Tier",
        labels={'x': 'Income Tier', 'y': 'Default Rate (%)'},
        color=default_by_income.values,
        color_continuous_scale='RdYlGn_r'
    )
    fig4.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Risk Predictor ────────────────────────────────
st.subheader("🎯 Customer Risk Predictor")
st.markdown("Customer details daalo — live risk score milega Flask API se")

col_a, col_b, col_c = st.columns(3)

with col_a:
    age = st.slider("Age", 18, 90, 35)
    monthly_income = st.slider("Monthly Income ($)", 0, 50000, 5000, step=500)
    debt_ratio = st.slider("Debt Ratio", 0.0, 3.0, 0.3, step=0.05)

with col_b:
    revolving = st.slider("Credit Utilization (0-1)", 0.0, 1.0, 0.3, step=0.05)
    open_loans = st.slider("Open Credit Lines", 0, 20, 4)
    dependents = st.slider("Number of Dependents", 0, 10, 1)

with col_c:
    late_30_59 = st.slider("30-59 Days Late (times)", 0, 10, 0)
    late_60_89 = st.slider("60-89 Days Late (times)", 0, 10, 0)
    late_90 = st.slider("90+ Days Late (times)", 0, 10, 0)
    real_estate = st.slider("Real Estate Loans", 0, 10, 1)

if st.button("🔍 Predict Risk", type="primary"):
    payload = {
        "Unnamed: 0": 0,
        "RevolvingUtilizationOfUnsecuredLines": revolving,
        "age": age,
        "NumberOfTime30-59DaysPastDueNotWorse": late_30_59,
        "DebtRatio": debt_ratio,
        "MonthlyIncome": monthly_income,
        "NumberOfOpenCreditLinesAndLoans": open_loans,
        "NumberOfTimes90DaysLate": late_90,
        "NumberRealEstateLoansOrLines": real_estate,
        "NumberOfTime60-89DaysPastDueNotWorse": late_60_89,
        "NumberOfDependents": dependents
    }

    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=payload,
            timeout=10
        )
        result = response.json()

        risk_label = result['risk_label']
        risk_score = result['risk_score']

        if risk_label == "Low Risk":
            color = "🟢"
            st.success(f"{color} **{risk_label}** — Risk Score: {risk_score}/100")
        elif risk_label == "Medium Risk":
            color = "🟡"
            st.warning(f"{color} **{risk_label}** — Risk Score: {risk_score}/100")
        else:
            color = "🔴"
            st.error(f"{color} **{risk_label}** — Risk Score: {risk_score}/100")

        st.metric("Default Probability", f"{result['default_probability']*100:.1f}%")

    except Exception as e:
        st.error(f"API connection failed: {e}")
        st.info("Make sure Flask API is running on localhost:5000")

# ── Footer ────────────────────────────────────────
st.divider()
st.caption("RiskLens — Financial Risk Analytics Platform | Python + Flask + Streamlit + SHAP")