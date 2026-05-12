import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

#  Transaction types to process 
TRANSACTION_TYPES = [
    "Wire Transfer",
    "FX Conversion",
    "Equity Trade",
    "Bond Settlement",
    "Derivative Contract",
    "Interbank Transfer",
    "Corporate Payment",
    "Structured Product"
]

CURRENCIES = ["ZAR", "USD", "EUR", "GBP", "JPY"]

ACCOUNTS = [f"ACC{str(i).zfill(5)}" for i in range(1, 51)]  # 50 mock accounts


def generate_transaction(anomaly=False):
    """
    Generate a single transaction.
    If anomaly=True, the transaction will have suspicious characteristics:
    - Unusually large amount
    - Odd hours (2am - 4am)
    - Rapid repeat from same account
    """
    now = datetime.now()

    if anomaly:
        # Suspicious transaction characteristics
        amount = round(random.uniform(500_000, 5_000_000), 2)   # Very large
        hour = random.choice([2, 3, 4])                          # Middle of night
        minute = random.randint(0, 59)
        timestamp = now.replace(hour=hour, minute=minute)
        account = random.choice(ACCOUNTS[:5])                    # Few accounts, repeated
        currency = random.choice(["USD", "EUR"])                 # Foreign currency spike
    else:
        # Normal transaction
        amount = round(random.uniform(1_000, 150_000), 2)
        timestamp = now - timedelta(minutes=random.randint(0, 60))
        account = random.choice(ACCOUNTS)
        currency = random.choice(CURRENCIES)

    return {
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "transaction_id": f"TXN{random.randint(100000, 999999)}",
        "account": account,
        "type": random.choice(TRANSACTION_TYPES),
        "amount": amount,
        "currency": currency,
        "hour_of_day": timestamp.hour,
        "is_foreign": 1 if currency != "ZAR" else 0,
    }


def generate_transaction_batch(n=100, anomaly_rate=0.08):
    """
    Generate a batch of n transactions.
    anomaly_rate = proportion that are suspicious (default 8%)
    Returns a pandas DataFrame.
    """
    transactions = []
    for _ in range(n):
        is_anomaly = random.random() < anomaly_rate
        transactions.append(generate_transaction(anomaly=is_anomaly))

    df = pd.DataFrame(transactions)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp", ascending=False).reset_index(drop=True)
    return df
