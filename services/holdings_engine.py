# services/holdings_engine.py

import requests
import pandas as pd


def get_holdings_trend(symbol: str, num_periods: int = 3) -> dict:
    """
    Scrapes Screener.in's Shareholding Pattern page to get
    the last `num_periods` quarterly holdings for Promoter, FII, DII (Mutual Funds).
    Returns {} if unsuccessful.
    """
    base = symbol.split('.')[0].upper()
    url = f"https://www.screener.in/company/{base}/shareholding/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        # Read all tables from the page
        dfs = pd.read_html(resp.text)
    except Exception:
        return {}

    # Find the table that has the shareholding columns
    table = None
    for df in dfs:
        cols = [c.lower() for c in df.columns]
        if 'promoters' in cols and 'fii' in cols and 'mutual funds' in cols:
            table = df
            break

    if table is None or table.empty:
        return {}

    # Keep and rename only the relevant columns
    df = table[['Quarter', 'Promoters', 'FII', 'Mutual Funds']].copy()
    df.columns = ['Quarter', 'Promoter', 'FII', 'DII']

    # Strip '%' and convert to float
    for col in ['Promoter', 'FII', 'DII']:
        df[col] = (
            df[col]
            .astype(str)
            .str.rstrip('%')
            .replace('', '0')
            .astype(float)
        )

    # Take the last num_periods rows
    df = df.tail(num_periods)

    return {
        'years':    df['Quarter'].tolist(),
        'promoter': df['Promoter'].tolist(),
        'fii':      df['FII'].tolist(),
        'dii':      df['DII'].tolist(),
    }
