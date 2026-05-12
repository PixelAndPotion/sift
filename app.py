import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

from transaction_gen import generate_transaction_batch
from anomaly_detector import train_detector, score_transactions, get_summary_stats
from report_gen import generate_report

# Page config — must be first Streamlit call
st.set_page_config(
    page_title="SIFT — Signal Intelligence for Financial Transactions",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS 
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #F0F4FF; }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #0033A0, #0052CC);
        padding: 24px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
        color: white;
    }
    .main-header h1 { color: white; font-size: 2.2rem; margin: 0; letter-spacing: 2px; }
    .main-header p { color: #A8C4E8; margin: 4px 0 0 0; font-size: 0.95rem; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        border-left: 4px solid #0033A0;
    }

    /* Section headers */
    .section-header {
        color: #0033A0;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        border-bottom: 2px solid #0033A0;
        padding-bottom: 6px;
        margin: 24px 0 16px 0;
    }

    /* Risk badges */
    .risk-critical { color: #B41E1E; font-weight: bold; }
    .risk-high     { color: #C86400; font-weight: bold; }
    .risk-medium   { color: #B48A00; font-weight: bold; }
    .risk-low      { color: #00783C; font-weight: bold; }

    /* Alert box */
    .alert-box {
        background: #FFF5F5;
        border: 1px solid #FEB2B2;
        border-left: 4px solid #B41E1E;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
    }

    /* Sidebar */
    .css-1d391kg { background-color: #001F6B; }
</style>
""", unsafe_allow_html=True)


#  Sidebar controls
with st.sidebar:
    st.markdown("## ⚙️ SIFT Controls")
    st.markdown("---")

    n_transactions = st.slider(
        "Transactions to analyse",
        min_value=50, max_value=500, value=150, step=25,
        help="Number of simulated transactions to generate and analyse"
    )

    anomaly_rate = st.slider(
        "Simulated anomaly rate",
        min_value=0.02, max_value=0.20, value=0.08, step=0.01,
        format="%.0f%%",
        help="Proportion of transactions that will be suspicious"
    )

    auto_refresh = st.toggle("Auto-refresh (live feed)", value=False)
    refresh_interval = st.slider("Refresh interval (seconds)", 5, 30, 10) if auto_refresh else None

    st.markdown("---")
    st.markdown("**SIFT v1.0**")
    st.markdown("Signal Intelligence for Financial Transactions")
    st.markdown("*Built by Arika Bharath*")


#  Main header
st.markdown("""
<div class="main-header">
    <h1>🔍 SIFT</h1>
    <p>Signal Intelligence for Financial Transactions  ·  Real-Time Risk Monitoring Dashboard</p>
</div>
""", unsafe_allow_html=True)


#  Generate and score transactions
@st.cache_data(ttl=5)  # Cache for 5 seconds — refreshes on auto-refresh
def load_and_score(n, rate):
    """Generate transactions, train model, score everything."""
    df = generate_transaction_batch(n=n, anomaly_rate=rate)
    model, scaler = train_detector(df)
    df_scored = score_transactions(df, model, scaler)
    summary = get_summary_stats(df_scored)
    return df_scored, summary

df, summary = load_and_score(n_transactions, anomaly_rate)


# KPI metric cards
st.markdown('<div class="section-header">Live Risk Overview</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Total Transactions", summary["total_transactions"])
with col2:
    st.metric("Anomalies Detected", summary["anomalies_detected"], delta=f"{summary['anomaly_rate']} rate", delta_color="inverse")
with col3:
    st.metric("🔴 Critical", summary["critical_alerts"])
with col4:
    st.metric("🟠 High", summary["high_alerts"])
with col5:
    st.metric("Flagged Value", summary["flagged_value"])
with col6:
    st.metric("Clean Transactions", summary["total_transactions"] - summary["anomalies_detected"])


#  Charts row 
st.markdown('<div class="section-header">Transaction Analytics</div>', unsafe_allow_html=True)

chart_col1, chart_col2, chart_col3 = st.columns([2, 1, 1])

with chart_col1:
    # Transaction amount scatter — coloured by risk level
    fig_scatter = px.scatter(
        df,
        x="timestamp",
        y="amount",
        color="risk_level",
        color_discrete_map={
            "🔴 Critical": "#B41E1E",
            "🟠 High":     "#C86400",
            "🟡 Medium":   "#B48A00",
            "🟢 Low":      "#00783C",
        },
        title="Transaction Amounts Over Time — Risk Coloured",
        labels={"amount": "Amount (R)", "timestamp": "Time", "risk_level": "Risk Level"},
        hover_data=["transaction_id", "account", "type", "currency"]
    )
    fig_scatter.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font_color="#0033A0",
        height=320
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with chart_col2:
    # Risk level donut chart
    risk_counts = df["risk_level"].value_counts().reset_index()
    risk_counts.columns = ["Risk Level", "Count"]
    fig_donut = px.pie(
        risk_counts,
        values="Count",
        names="Risk Level",
        title="Risk Distribution",
        hole=0.55,
        color="Risk Level",
        color_discrete_map={
            "🔴 Critical": "#B41E1E",
            "🟠 High":     "#C86400",
            "🟡 Medium":   "#B48A00",
            "🟢 Low":      "#00783C",
        }
    )
    fig_donut.update_layout(
        paper_bgcolor="white",
        title_font_color="#0033A0",
        height=320,
        showlegend=False
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with chart_col3:
    # Transactions by hour of day — spots the 3am spike
    hour_risk = df.groupby("hour_of_day")["is_anomaly"].agg(["sum", "count"]).reset_index()
    hour_risk.columns = ["hour", "anomalies", "total"]
    fig_hour = px.bar(
        hour_risk,
        x="hour",
        y="anomalies",
        title="Anomalies by Hour of Day",
        labels={"hour": "Hour (24h)", "anomalies": "Anomalies"},
        color="anomalies",
        color_continuous_scale=["#00783C", "#C86400", "#B41E1E"]
    )
    fig_hour.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font_color="#0033A0",
        height=320,
        showlegend=False
    )
    st.plotly_chart(fig_hour, use_container_width=True)


#  Critical alerts feed 
st.markdown('<div class="section-header">🔴 Critical & High Alerts</div>', unsafe_allow_html=True)

critical_df = df[df["risk_level"].isin(["🔴 Critical", "🟠 High"])].copy()
critical_df = critical_df.sort_values("anomaly_score").head(10)

if len(critical_df) > 0:
    for _, row in critical_df.iterrows():
        risk_emoji = "🔴" if "Critical" in row["risk_level"] else "🟠"
        st.markdown(f"""
        <div class="alert-box">
            <strong>{risk_emoji} {row['risk_level'].split()[-1]} ALERT</strong>  ·
            <strong>{row['transaction_id']}</strong>  ·
            Account: <code>{row['account']}</code>  ·
            Type: {row['type']}  ·
            Amount: <strong>R{row['amount']:,.2f} {row['currency']}</strong>  ·
            Time: {str(row['timestamp'])[:16]}  ·
            Hour: {row['hour_of_day']}:00
        </div>
        """, unsafe_allow_html=True)
else:
    st.success("No Critical or High alerts in this batch.")


#  Full scored transaction table 
st.markdown('<div class="section-header">All Transactions</div>', unsafe_allow_html=True)

show_anomalies_only = st.checkbox("Show flagged transactions only", value=False)
display_df = df[df["is_anomaly"]] if show_anomalies_only else df

display_cols = ["timestamp", "transaction_id", "account", "type", "amount", "currency", "risk_level", "anomaly_score"]
st.dataframe(
    display_df[display_cols].rename(columns={
        "timestamp": "Time",
        "transaction_id": "TXN ID",
        "account": "Account",
        "type": "Type",
        "amount": "Amount (R)",
        "currency": "CCY",
        "risk_level": "Risk Level",
        "anomaly_score": "Anomaly Score"
    }),
    use_container_width=True,
    height=300
)


#  Download PDF report 
st.markdown('<div class="section-header">Risk Report</div>', unsafe_allow_html=True)

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
        with st.spinner("Generating SIFT risk report..."):
            pdf_bytes = generate_report(df, summary)
            st.download_button(
                label="⬇️ Download Report",
                data=pdf_bytes,
                file_name=f"SIFT_Risk_Report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        st.success("Report ready. Click Download above.")


#  Auto refresh 
if auto_refresh:
    time.sleep(refresh_interval)
    st.cache_data.clear()
    st.rerun()
