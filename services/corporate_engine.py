# services/corporate_engine.py
import requests
from datetime import datetime

def get_corporate_calendar(symbol: str) -> dict:
    """
    Fetch upcoming corporate events for an NSE equity:
      - Earnings Date (first “Results” announcement)
      - Ex-Dividend Date (first “Ex-Dividend” announcement)
    Shareholding Changes remains 'N/A' until a reliable data source is added.
    """
    sym = symbol.upper()
    ann_url = f"https://www.nseindia.com/api/corporate-announcements?symbol={sym}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": f"https://www.nseindia.com/get-quotes/equity?symbol={sym}",
    }

    earnings_date       = "N/A"
    ex_dividend_date    = "N/A"
    shareholding_changes = "N/A"

    sess = requests.Session()
    try:
        # Warm up session & cookies
        sess.get("https://www.nseindia.com", headers=headers, timeout=5)
        sess.get(ann_url, headers=headers, timeout=5)
        # Fetch announcements JSON
        resp = sess.get(ann_url, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        # Data may sit under 'records'->'data' or directly under 'data'
        items = data.get("records", {}).get("data", []) or data.get("data", [])
        for item in items:
            title    = item.get("title", "").lower()
            date_str = item.get("announcementDate", "")
            # Convert '10-May-2025' → '2025-05-10'
            try:
                dt = datetime.strptime(date_str, "%d-%b-%Y").strftime("%Y-%m-%d")
            except Exception:
                continue

            if "results" in title and earnings_date == "N/A":
                earnings_date = dt
            if "ex-dividend" in title and ex_dividend_date == "N/A":
                ex_dividend_date = dt

    except Exception:
        # On any error, leave as N/A
        pass

    return {
        "earnings_date": earnings_date,
        "ex_dividend_date": ex_dividend_date,
        "shareholding_changes": shareholding_changes
    }
