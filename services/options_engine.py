# services/options_engine.py
import pandas as pd
from nsepython import nse_optionchain_scrapper

def get_option_chain(symbol: str) -> pd.DataFrame:
    """
    Fetch option chain data for an NSE equity symbol via nsepython.
    Returns a DataFrame with columns:
      - strike
      - call_open_interest
      - put_open_interest
    """
    data = nse_optionchain_scrapper(symbol.upper())
    records = []
    for itm in data.get("records", {}).get("data", []):
        strike = itm.get("strikePrice")
        ce     = itm.get("CE", {})
        pe     = itm.get("PE", {})
        records.append({
            "strike": strike,
            "call_open_interest": ce.get("openInterest", 0),
            "put_open_interest":  pe.get("openInterest", 0),
        })
    return pd.DataFrame(records)
