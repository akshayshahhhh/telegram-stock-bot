import yfinance as yf


def get_fundamentals(symbol: str) -> dict:
    """
    Fetches key fundamental metrics for a given stock symbol using yfinance.
    Automatically appends '.NS' if no exchange suffix is present.

    Returns:
        dict: Fundamental metrics including market cap, P/E ratios, P/B, dividend yield, ROE, EPS.
    """
    yf_symbol = symbol if "." in symbol else f"{symbol}.NS"
    ticker = yf.Ticker(yf_symbol)
    info = ticker.info or {}
    return {
        'market_cap':       info.get('marketCap'),
        'trailing_pe':      info.get('trailingPE'),
        'forward_pe':       info.get('forwardPE'),
        'price_to_book':    info.get('priceToBook'),
        'dividend_yield':   info.get('dividendYield'),
        'return_on_equity': info.get('returnOnEquity'),
        'debt_to_equity':   info.get('debtToEquity'),
        'eps_ttm':          info.get('trailingEps'),
    }


def get_annual_fundamentals(symbol: str, num_years: int = 4) -> dict:
    """
    Fetches the last `num_years` of Revenue and PAT for a given symbol.
    Tries yfinance's earnings first; if not available or insufficient, falls back to financials.

    Args:
        symbol (str): Stock symbol (e.g., 'TCS' or 'TCS.NS').
        num_years (int): Number of years of data to fetch (default 4).

    Returns:
        dict: {
            'years': [Y1, Y2, ...],
            'revenue': [R1, R2, ...],
            'pat': [P1, P2, ...]
        } or {} if insufficient data.
    """
    yf_symbol = symbol if "." in symbol else f"{symbol}.NS"
    ticker = yf.Ticker(yf_symbol)

    # Attempt to use the earnings DataFrame
    df_earn = ticker.earnings
    if df_earn is not None and not df_earn.empty:
        df_sel = df_earn.tail(num_years)
        years   = df_sel.index.tolist()
        revenue = df_sel['Revenue'].tolist()
        pat     = df_sel['Earnings'].tolist()
    else:
        # Fallback to annual financials
        fin = ticker.financials
        if fin is None or fin.empty or 'Total Revenue' not in fin.index or 'Net Income' not in fin.index:
            return {}
        cols = list(fin.columns)[:num_years]
        years   = [col.year for col in cols]
        revenue = fin.loc['Total Revenue', cols].tolist()
        pat     = fin.loc['Net Income', cols].tolist()

    if not years or not revenue or not pat:
        return {}

    return {
        'years': years,
        'revenue': revenue,
        'pat': pat,
    }
