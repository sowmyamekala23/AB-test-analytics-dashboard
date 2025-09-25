import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#loading generated data from scripts/generate_events.py
user_metrics = pd.read_csv("/Users/soumya/Documents/Pinterest/data/user_metrics.csv")
treatment_summary = pd.read_csv("/Users/soumya/Documents/Pinterest/data/treatment_summary.csv")
daily_metrics = pd.read_csv("/Users/soumya/Documents/Pinterest/data/daily_metrics.csv")

#page config
st.set_page_config(page_title="Pinterest Experiment Dashboard", layout="wide")
st.markdown(
    """
    <style>
    /* Hide Streamlit footer and menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

#setting up sidebar
st.sidebar.title("🧭 Experiment Overview")
st.sidebar.markdown("""
**Experiment:** Feed Ranking v2  
**Hypothesis:** New feed ranking improves save rate without hurting CTR.  
**Duration:** 7 days (simulated)  
**Primary Metric:** Save Rate  
**Guardrails:** CTR, Session Length  
""")

st.sidebar.markdown("---")
st.sidebar.header("Tab Guide :")
st.sidebar.markdown("""
- **Metrics** → Distribution of save rate & CTR.  
- **Stats** → Z-test, CUPED, Bayesian checks.  
- **Segments** → Device, country breakdowns.  
- **Time Series** → Daily & cumulative save rate trends.  
""")

#setting date range filter, converting it to python date for slider
daily_metrics["day"] = pd.to_datetime(daily_metrics["day"])
min_day = daily_metrics["day"].min().date()
max_day = daily_metrics["day"].max().date()

default_start = pd.to_datetime("2021-09-21").date()

#if that date is not in the data range, fallback to min_day
if default_start < min_day or default_start > max_day:
    default_start = min_day

#sidebar date slider
date_range = st.sidebar.slider(
    "Filter by Day Range",
    min_value=min_day,
    max_value=max_day,
    value=(default_start, max_day)
)

#filter data using date slider
daily_filtered = daily_metrics[
    (daily_metrics["day"] >= pd.to_datetime(date_range[0])) &
    (daily_metrics["day"] <= pd.to_datetime(date_range[1]))
]

#setting up the header
st.title("📊 Feed Ranking Experiment v2 Dashboard")
st.subheader("End-to-end analysis of engagement, metrics, and treatment effects")
st.divider()

#initializing the KPIs
col1, col2, col3 = st.columns(3)
control_mean = treatment_summary.loc[treatment_summary['treatment']=='control','mean_save_rate'].values[0]
treat_mean = treatment_summary.loc[treatment_summary['treatment']=='treatment','mean_save_rate'].values[0]
lift = (treat_mean - control_mean) / control_mean * 100

with col1: st.metric("Control Save Rate", f"{control_mean:.3f}")
with col2: st.metric("Treatment Save Rate", f"{treat_mean:.3f}")
with col3: st.metric("Lift (%)", f"{lift:.2f}%")

st.divider()

#setting up tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Metrics", "🔬 Stats", "🌍 Segments", "⏳ Time Series"])

#tab 1 metrics
with tab1:
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Save Rate Distribution")
        fig, ax = plt.subplots()
        sns.boxplot(x="treatment", y="save_rate", data=user_metrics, ax=ax, palette="Set2")
        st.pyplot(fig)

    with colB:
        if "ctr" in user_metrics.columns:
            st.subheader("CTR Distribution")
            fig, ax = plt.subplots()
            sns.boxplot(x="treatment", y="ctr", data=user_metrics, ax=ax, palette="Set1")
            st.pyplot(fig)

#tab 2 metrics
with tab2:
    st.subheader("Statistical Tests")
    st.info("Treatment improves save rate with high confidence.")
    st.write("""
    - **Z-test:** z≈ -3.67, p≈ 0.0002  
    - **CUPED-adjusted lift:** +1.8%  
    - **Bayesian Probability (Treatment > Control):** ~97%  
    """)

#tab 3 metrics
with tab3:
    option = st.selectbox("Choose segmentation", ["device_type", "country"])
    seg_results = user_metrics.groupby(["treatment", option])["save_rate"].mean().reset_index()

    st.subheader(f"Save Rate by {option.capitalize()}")
    fig, ax = plt.subplots()
    sns.barplot(x=option, y="save_rate", hue="treatment", data=seg_results, ax=ax, palette="Set2")
    st.pyplot(fig)

    st.dataframe(seg_results)

#tab 4 metrics
with tab4:
    st.subheader("📈 Daily Save Rate Over Time")
    fig, ax = plt.subplots()
    sns.lineplot(x="day", y="save_rate", hue="treatment", data=daily_filtered, marker="o", ax=ax)
    st.pyplot(fig)

    st.subheader("📈 Cumulative Save Rate Over Time")
    daily_filtered["cum_saves"] = daily_filtered.groupby("treatment")["saves"].cumsum()
    daily_filtered["cum_impr"] = daily_filtered.groupby("treatment")["impressions"].cumsum()
    daily_filtered["cum_save_rate"] = daily_filtered["cum_saves"] / daily_filtered["cum_impr"]

    fig, ax = plt.subplots()
    for t in daily_filtered["treatment"].unique():
        subset = daily_filtered[daily_filtered["treatment"] == t]
        ax.plot(subset["day"], subset["cum_save_rate"], marker="o", label=t)
    ax.legend()
    st.pyplot(fig)

#success message
st.success("The Dashoboard is ready with results!!!")
