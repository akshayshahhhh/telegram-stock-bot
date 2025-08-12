# utils/indicators.py

import pandas as pd

def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    latest_rsi = rsi.iloc[-1]
    return round(latest_rsi, 2) if not pd.isna(latest_rsi) else 0.0

def calculate_ema(prices: pd.Series, period: int) -> float:
    ema = prices.ewm(span=period, adjust=False).mean()
    return round(ema.iloc[-1], 2)
