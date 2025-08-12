# services/screener_cache.py

import requests
import json
import os

CACHE_DIR = "services/earnings_cache"

def get_cached_earnings(symbol):
    os.makedirs(CACHE_DIR, exist_ok=True)
    file_path = os.path.join(CACHE_DIR, f"{symbol.upper()}.json")

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)

    data = fetch_earnings_from_screener(symbol)
    if data:
        with open(file_path, "w") as f:
            json.dump(data, f)
    return data

def fetch_earnings_from_screener(symbol):
    try:
        url = f"https://www.screener.in/company/{symbol.upper()}/consolidated/"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None

        # Placeholder dummy response (replace with your real logic to parse Screener page if needed)
        # For now, return dummy 3-year earnings
        return {
            "year_1": {"revenue": "12,000 Cr", "pat": "1,000 Cr", "growth": "15%"},
            "year_2": {"revenue": "13,800 Cr", "pat": "1,300 Cr", "growth": "30%"},
            "year_3": {"revenue": "15,200 Cr", "pat": "1,600 Cr", "growth": "23%"},
        }

    except Exception as e:
        return None
