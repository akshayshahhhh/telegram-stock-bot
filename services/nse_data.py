import yfinance as yf
import pandas as pd

def get_ohlcv(symbol: str) -> pd.DataFrame:
    """
    Fetches the OHLCV data for a given symbol from Yahoo Finance (NSE).
    Returns a DataFrame with lowercase columns: open, high, low, close, volume.
    Handles MultiIndex columns from yfinance and strips ticker suffix.
    """
    # Ensure NSE suffix
    yf_symbol = symbol if symbol.upper().endswith('.NS') else symbol.upper() + '.NS'
    # Download raw data without auto-adjust to keep OHLCV
    df = yf.download(
        yf_symbol,
        period="6mo",
        interval="1d",
        progress=False,
        auto_adjust=False
    )

    # Validate
    if df is None or df.empty or not isinstance(df, pd.DataFrame):
        return pd.DataFrame()

    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(map(str, col)).strip() for col in df.columns.values]
    else:
        df.columns = list(df.columns)

    # Strip suffix after underscore (ticker) and lowercase
    df.columns = [col.split('_')[0].lower() for col in df.columns]

    # Select only needed columns
    needed = ['open', 'high', 'low', 'close', 'volume']
    if not all(col in df.columns for col in needed):
        print(f"❌ Missing expected OHLCV columns. Available: {list(df.columns)}")
        return pd.DataFrame()
    df = df[needed]

    # Ensure datetime index
    df.index = pd.to_datetime(df.index)

    return df
