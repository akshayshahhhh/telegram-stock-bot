import pandas as pd
from services.nse_data import get_ohlcv

# Fetches raw OHLCV DataFrame; returns a DataFrame or an error dict

def get_stock_data(symbol):
    # Get raw data
    df = get_ohlcv(symbol)

    print("🔍 get_ohlcv() returned:", type(df))

    # Handle string error
    if isinstance(df, str):
        print(f"❌ ERROR: Received string instead of DataFrame for {symbol}")
        return {"error": f"Invalid data format received for {symbol}"}

    # Handle None or non-DataFrame
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        print(f"❌ ERROR: No valid OHLCV data for {symbol}")
        return {"error": f"No valid OHLCV data for {symbol}"}

    # OK
    print("✅ Data is clean, returning DataFrame for analysis")
    return df