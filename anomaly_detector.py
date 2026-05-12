import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


#  Features the model uses to detect anomalies 
# These are the numeric signals that reveal suspicious behaviour:
# - amount:       unusually large amounts are a red flag
# - hour_of_day:  transactions at 3am are suspicious
# - is_foreign:   foreign currency spikes can indicate risk
FEATURE_COLUMNS = ["amount", "hour_of_day", "is_foreign"]


def train_detector(df: pd.DataFrame):
    """
    Train an Isolation Forest on the transaction data.
    Returns the trained model and the fitted scaler.

    Isolation Forest works by randomly partitioning data.
    Anomalies are isolated faster (fewer splits needed)
    so they get lower anomaly scores.

    contamination=0.08 means we expect ~8% of transactions to be anomalous.
    """
    features = df[FEATURE_COLUMNS].copy()

    # Scale features so amount (in millions) doesn't dominate hour_of_day (0-23)
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    model = IsolationForest(
        n_estimators=100,       # Number of trees in the forest
        contamination=0.08,     # Expected proportion of anomalies
        random_state=42,        # Reproducible results
        n_jobs=-1               # Use all CPU cores
    )
    model.fit(features_scaled)
    return model, scaler


def score_transactions(df: pd.DataFrame, model, scaler):
    """
    Score every transaction in the DataFrame.
    Adds three new columns:
    - anomaly_score:  raw score from Isolation Forest (-1 to 1, lower = more anomalous)
    - is_anomaly:     True/False flag
    - risk_level:     Human-readable risk label (Low / Medium / High / Critical)
    """
    features = df[FEATURE_COLUMNS].copy()
    features_scaled = scaler.transform(features)

    # -1 = anomaly, 1 = normal (sklearn convention)
    predictions = model.predict(features_scaled)

    # Raw decision scores — more negative = more anomalous
    scores = model.decision_function(features_scaled)

    df = df.copy()
    df["anomaly_score"] = scores
    df["is_anomaly"] = predictions == -1

    # Map scores to human-readable risk levels
    df["risk_level"] = df["anomaly_score"].apply(_score_to_risk)

    return df


def _score_to_risk(score):
    """
    Convert the raw Isolation Forest score to a risk label.
    Scores are negative for anomalies — more negative = higher risk.
    Thresholds tuned for financial transaction context.
    """
    if score < -0.15:
        return "🔴 Critical"
    elif score < -0.05:
        return "🟠 High"
    elif score < 0.05:
        return "🟡 Medium"
    else:
        return "🟢 Low"


def get_summary_stats(df: pd.DataFrame):
    """
    Return a summary dictionary for the dashboard header cards.
    """
    total = len(df)
    anomalies = df["is_anomaly"].sum()
    critical = (df["risk_level"] == "🔴 Critical").sum()
    high = (df["risk_level"] == "🟠 High").sum()
    flagged_value = df[df["is_anomaly"]]["amount"].sum()

    return {
        "total_transactions": total,
        "anomalies_detected": int(anomalies),
        "critical_alerts": int(critical),
        "high_alerts": int(high),
        "flagged_value": f"R{flagged_value:,.2f}",
        "anomaly_rate": f"{(anomalies/total*100):.1f}%"
    }
