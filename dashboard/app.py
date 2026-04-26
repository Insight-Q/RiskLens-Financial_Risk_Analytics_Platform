import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import joblib
import shap
import matplotlib.pyplot as plt
import os

# Session state init
if "prediction_result" not in st.session_state:
    st.session_state["prediction_result"] = None

if "stay_on_predictor" not in st.session_state:
    st.session_state["stay_on_predictor"] = False
# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Loan Default Risk Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS  (dark financial theme)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@300;400;600;700&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
    background-color: #0d0f1a;
    color: #e8eaf0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #111427 0%, #0d0f1a 100%);
    border-right: 1px solid #1e2240;
}
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #a0a8cc !important;
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(135deg, #141728 0%, #1a1f38 100%);
    border: 1px solid #252b4a;
    border-radius: 16px;
    padding: 28px 24px;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(99, 130, 255, 0.15);
}
.kpi-label {
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b74a8;
    margin-bottom: 8px;
    font-family: 'DM Mono', monospace;
}
.kpi-value {
    font-size: 2.4rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 4px;
}
.kpi-sub {
    font-size: 0.75rem;
    color: #555e8a;
    font-family: 'DM Mono', monospace;
}
.accent-teal   { color: #2dd4bf; }
.accent-red    { color: #f87171; }
.accent-violet { color: #a78bfa; }

/* Section headers */
.section-header {
    font-size: 0.7rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #3d4570;
    font-family: 'DM Mono', monospace;
    margin-bottom: 4px;
}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid #1e2240;
    margin: 12px 0 24px 0;
}

/* Main title */
.main-title {
    font-size: 1.9rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #ffffff;
}
.main-sub {
    font-size: 0.85rem;
    color: #555e8a;
    font-family: 'DM Mono', monospace;
    margin-top: -6px;
}
/* Sidebar radio buttons hover */
section[data-testid="stSidebar"] .stRadio > div {
    padding: 8px;
    border-radius: 8px;
    transition: all 0.2s ease-in-out;
}

section[data-testid="stSidebar"] .stRadio > div:hover {
    background-color: rgba(45, 212, 191, 0.1);
}

/* Selected option highlight */
section[data-testid="stSidebar"] .stRadio label[data-checked="true"] {
    background-color: rgba(45, 212, 191, 0.15);
    border-left: 3px solid #2dd4bf;
    padding-left: 6px;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    """
    Attempt PostgreSQL connection first; fall back to the cleaned CSV
    so the dashboard remains functional in all environments.
    """
    try:
        from sqlalchemy import create_engine
        engine = create_engine(
            "postgresql://postgres:YOUR_PASSWORD@localhost:5432/loan_risk_db"
        )
        df = pd.read_sql("SELECT * FROM loans", engine)
        return df, "PostgreSQL"
    except Exception:
        import pathlib
        candidate_paths = [
            "../data/cs-training-clean.csv",
            "data/cs-training-clean.csv",
            "cs-training-clean.csv",
        ]
        for path in candidate_paths:
            if pathlib.Path(path).exists():
                df = pd.read_csv(path)
                # Drop unnamed index column if present
                if df.columns[0].startswith("Unnamed"):
                    df = df.iloc[:, 1:]
                return df, "CSV"
        raise FileNotFoundError(
            "Dataset not found. Ensure 'cs-training-clean.csv' exists in the data/ directory."
        )

df_raw, source = load_data()

# ─────────────────────────────────────────────
#  LOAD ML MODEL
# ─────────────────────────────────────────────
@st.cache_resource
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "../models/best_model_compressed.joblib")
    model = joblib.load(model_path)
    return model

model = load_model()

# ─────────────────────────────────────────────
#  SIDEBAR — FILTERS
# ─────────────────────────────────────────────

with st.sidebar:
    st.sidebar.markdown(
    "<h2 style='margin-bottom:10px;'>🎛️ Filters</h2>",
    unsafe_allow_html=True
    )
    
    st.markdown("---")

    age_min, age_max = int(df_raw["age"].min()), int(df_raw["age"].max())
    age_range = st.slider(
        "Age Range",
        min_value=age_min,
        max_value=age_max,
        value=(25, 70),
        step=1,
    )

    st.markdown("---")

    income_options = ["All", "Low (<2k)", "Mid (2k-5k)", "High (5k-10k)", "Very High (10k+)"]
    income_filter = st.selectbox("Monthly Income Tier", income_options)

    st.markdown("---")

    page = st.sidebar.radio("Navigation", ["Analytics Dashboard", "Risk Predictor"])

    st.markdown("---")

    default_filter = st.radio(
        "Default Status",
        ["All Customers", "Defaulters Only", "Non-Defaulters Only"],
    )



# ─────────────────────────────────────────────
#  APPLY FILTERS
# ─────────────────────────────────────────────
df = df_raw.copy()

df = df[(df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]

if income_filter != "All":
    bins   = [0, 2000, 5000, 10000, float("inf")]
    labels = ["Low (<2k)", "Mid (2k-5k)", "High (5k-10k)", "Very High (10k+)"]
    df["income_tier"] = pd.cut(df["MonthlyIncome"], bins=bins, labels=labels)
    df = df[df["income_tier"] == income_filter]

if default_filter == "Defaulters Only":
    df = df[df["SeriousDlqin2yrs"] == 1]
elif default_filter == "Non-Defaulters Only":
    df = df[df["SeriousDlqin2yrs"] == 0]

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
    <h1 style='text-align:center; margin-bottom:5px; font-size:36px;'>
    📊 Loan Risk Analytics Dashboard
    </h1>
    """, unsafe_allow_html=True)
st.markdown('<p class="main-sub" style="text-align:center;">Financial Risk Insights Dashboard</p>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)



if page == "Analytics Dashboard":
    # ─────────────────────────────────────────────
    #  KPI CARDS
    # ─────────────────────────────────────────────
    total_customers = len(df)
    default_rate    = df["SeriousDlqin2yrs"].mean() * 100
    avg_income      = df["MonthlyIncome"].median()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Customers</div>
            <div class="kpi-value accent-teal">{total_customers:,}</div>
            <div class="kpi-sub">after filters applied</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        color = "accent-red" if default_rate > 10 else "accent-violet"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Default Rate</div>
            <div class="kpi-value {color}">{default_rate:.2f}%</div>
            <div class="kpi-sub">SeriousDlqin2yrs = 1</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Median Monthly Income</div>
            <div class="kpi-value accent-violet">${avg_income:,.0f}</div>
            <div class="kpi-sub">USD · median (outliers excluded)</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    #  PLOTLY CHART THEME
    # ─────────────────────────────────────────────
    CHART_BG    = "#0d0f1a"
    PAPER_BG    = "#111427"
    GRID_COLOR  = "#1e2240"
    FONT_COLOR  = "#a0a8cc"
    ACCENT      = "#2dd4bf"
    ACCENT2     = "#f87171"
    ACCENT3     = "#a78bfa"

    def base_layout(title):
        return dict(
            title=dict(text=title, font=dict(color=FONT_COLOR, size=14, family="Sora")),
            plot_bgcolor=CHART_BG,
            paper_bgcolor=PAPER_BG,
            font=dict(color=FONT_COLOR, family="Sora"),
            xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
            yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
            margin=dict(l=20, r=20, t=50, b=20),
        )

    # ─────────────────────────────────────────────
    #  CHART 1 — Default Rate by Age Group
    # ─────────────────────────────────────────────
    st.markdown('<p class="section-header">📊 Default Rate Analysis</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        age_bins   = [0, 30, 45, 60, 200]
        age_labels = ["Under 30", "30-45", "46-60", "60+"]
        df_plot = df.copy()
        df_plot["age_group"] = pd.cut(df_plot["age"], bins=age_bins, labels=age_labels)
        age_grp = (
            df_plot.groupby("age_group", observed=True)["SeriousDlqin2yrs"]
            .agg(["mean", "count"])
            .reset_index()
        )
        age_grp["default_pct"] = age_grp["mean"] * 100

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=age_grp["age_group"],
            y=age_grp["default_pct"],
            marker=dict(
                color=age_grp["default_pct"],
                colorscale=[[0, "#1e3a5f"], [0.5, ACCENT3], [1, ACCENT2]],
                showscale=False,
            ),
            text=[f"{v:.1f}%" for v in age_grp["default_pct"]],
            textposition="outside",
            textfont=dict(color=FONT_COLOR, size=11),
        ))
        fig1.update_layout(
            **base_layout("Default Rate by Age Group"),
            yaxis_title="Default Rate (%)",
            showlegend=False,
        )
        st.plotly_chart(fig1, use_container_width=True)

    # ─────────────────────────────────────────────
    #  CHART 2 — Debt Ratio Boxplot
    # ─────────────────────────────────────────────
    with c2:
        df_box = df.copy()
        df_box["Status"] = df_box["SeriousDlqin2yrs"].map({0: "No Default", 1: "Defaulted"})
        # Cap extreme outliers for chart readability
        df_box = df_box[df_box["DebtRatio"] < 5]

        fig2 = go.Figure()
        for status, color in [("No Default", ACCENT), ("Defaulted", ACCENT2)]:
            subset = df_box[df_box["Status"] == status]
            fig2.add_trace(go.Box(
                y=subset["DebtRatio"],
                name=status,
                marker_color=color,
                line_color=color,
                fillcolor="rgba(45,212,191,0.2)" if color == ACCENT else "rgba(244,63,94,0.2)",
                boxmean=True,
            ))
        fig2.update_layout(
            **base_layout("Debt Ratio Distribution"),
            yaxis_title="Debt Ratio",
            showlegend=True,
            legend=dict(bgcolor=CHART_BG, bordercolor=GRID_COLOR),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ─────────────────────────────────────────────
    #  CHART 3 — Income vs Debt Ratio Scatter
    # ─────────────────────────────────────────────
    st.markdown('<p class="section-header">🔍 Income Risk Scatter</p>', unsafe_allow_html=True)

    df_scatter = df.copy().dropna(subset=["MonthlyIncome"])
    # Remove extreme outliers for scatter plot clarity
    df_scatter = df_scatter[
        (df_scatter["MonthlyIncome"] < 30000) &
        (df_scatter["DebtRatio"] < 3)
    ]
    # Sample for rendering performance (max 5,000 points)
    if len(df_scatter) > 5000:
        df_scatter = df_scatter.sample(5000, random_state=42)

    df_scatter["Default"] = df_scatter["SeriousDlqin2yrs"].map({0: "No Default", 1: "Defaulted"})

    fig3 = px.scatter(
        df_scatter,
        x="MonthlyIncome",
        y="DebtRatio",
        color="Default",
        color_discrete_map={"No Default": ACCENT, "Defaulted": ACCENT2},
        opacity=0.45,
        size_max=6,
        hover_data=["age", "NumberOfTimes90DaysLate"],
        labels={
            "MonthlyIncome": "Monthly Income (USD)",
            "DebtRatio": "Debt Ratio",
        },
    )
    fig3.update_layout(
        **base_layout("Monthly Income vs Debt Ratio — Default Risk"),
        legend=dict(bgcolor=CHART_BG, bordercolor=GRID_COLOR),
    )
    fig3.update_traces(marker=dict(size=5))
    st.plotly_chart(fig3, use_container_width=True)

if page == "Risk Predictor":
    st.markdown("### Customer Risk Predictor")
    st.markdown("Enter customer details to get a live default risk assessment.")

    col1, col2 = st.columns(2)

    with col1:
        age = st.slider("Age", 18, 90, 35)
        monthly_income = st.number_input("Monthly Income (USD)", 0, 100000, 5000, step=500)
        debt_ratio = st.slider("Debt Ratio", 0.0, 1.0, 0.3, step=0.01)
        revolving_utilization = st.slider("Revolving Credit Utilization", 0.0, 1.0, 0.3, step=0.01)

    with col2:
        dependents = st.number_input("Number of Dependents", 0, 10, 0)
        open_credit_lines = st.number_input("Open Credit Lines", 0, 30, 5)
        real_estate_loans = st.number_input("Real Estate Loans", 0, 10, 1)
        times_30_59 = st.number_input("Times 30-59 Days Late", 0, 10, 0)
        times_60_89 = st.number_input("Times 60-89 Days Late", 0, 10, 0)
        times_90_late = st.number_input("Times 90+ Days Late", 0, 10, 0)

    if st.button("Generate Risk Assessment", type="primary"):
        input_data = pd.DataFrame([{
            "Unnamed: 0": 0,
            "RevolvingUtilizationOfUnsecuredLines": revolving_utilization,
            "age": age,
            "NumberOfTime30-59DaysPastDueNotWorse": times_30_59,
            "DebtRatio": debt_ratio,
            "MonthlyIncome": monthly_income,
            "NumberOfOpenCreditLinesAndLoans": open_credit_lines,
            "NumberOfTimes90DaysLate": times_90_late,
            "NumberRealEstateLoansOrLines": real_estate_loans,
            "NumberOfTime60-89DaysPastDueNotWorse": times_60_89,
            "NumberOfDependents": dependents,
        }])
        input_data = input_data[model.feature_names_in_]
        proba = model.predict_proba(input_data)[0][1]
        st.session_state["prediction_result"] = {
            "proba": proba,
            "input_data": input_data,
        }
        st.session_state["stay_on_predictor"] = True
        st.rerun()

    # Results — session state se dikhao
    if st.session_state["prediction_result"] is not None:
        proba = st.session_state["prediction_result"]["proba"]
        input_data = st.session_state["prediction_result"]["input_data"]

        if proba < 0.15:
            risk_level, color = "Low Risk", "green"
        elif proba < 0.40:
            risk_level, color = "Medium Risk", "orange"
        else:
            risk_level, color = "High Risk", "red"

        st.markdown(f"""
        <div style="text-align:center; padding:24px; border-radius:12px; border: 1px solid {color}; margin: 16px 0;">
            <p style="font-size:0.8rem; color:gray; margin:0;">DEFAULT PROBABILITY</p>
            <p style="font-size:3rem; font-weight:700; color:{color}; margin:8px 0;">{proba*100:.1f}%</p>
            <p style="font-size:1.1rem; color:{color}; margin:0;">{risk_level}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### What drove this prediction?")
        try:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(input_data)
            sv = shap_values[:, :, 1]
            base_val = explainer.expected_value[1]
            explanation = shap.Explanation(
                values=sv[0],
                base_values=base_val,
                data=input_data.iloc[0].values,
                feature_names=list(input_data.columns)
            )
            fig, ax = plt.subplots(figsize=(10, 5))
            shap.plots.waterfall(explanation, show=False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        except Exception as e:
            st.warning(f"SHAP not available: {e}")

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;font-size:0.7rem;color:#2a2f4a;font-family:DM Mono,monospace;'>"
    "Financial Risk Analytics - Loan Default Prediction - Portfolio Project"
    "</p>",
    unsafe_allow_html=True,
)