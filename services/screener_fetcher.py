import requests
import json
from services.screener_cache import load_from_cache, save_to_cache

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_earnings_data(symbol: str):
    """
    Fetch last 3 years of earnings (Revenue, PAT) from Screener.in
    """
    cached = load_from_cache(symbol)
    if cached:
        return cached

    try:
        url = f"https://www.screener.in/company/{symbol}/consolidated/"
        response = requests.get(url, headers=HEADERS, timeout=10)

        if "Profit & Loss" not in response.text:
            return {"error": "Invalid Screener page or symbol"}

        start = response.text.find("Standalone")  # crude HTML split
        block = response.text[start:start+3000]

        lines = block.splitlines()
        earnings = []

        for line in lines:
            if "Revenue" in line and "Other" not in line:
                rev_line = line
            if "Net Profit" in line:
                pat_line = line

        # crude extraction – for real use, use BeautifulSoup
        rev_values = [int(s.replace(",", "")) for s in rev_line.split() if s.replace(",", "").isdigit()]
        pat_values = [int(s.replace(",", "")) for s in pat_line.split() if s.replace(",", "").isdigit()]

        for i in range(min(3, len(rev_values), len(pat_values))):
            earnings.append({
                "year": f"Year-{i+1}",
                "revenue": rev_values[-(i+1)],
                "pat": pat_values[-(i+1)],
                "growth": round(((pat_values[-(i+1)] / pat_values[-(i+2)]) - 1) * 100, 2) if i < len(pat_values) - 1 else None
            })

        save_to_cache(symbol, earnings)
        return earnings

    except Exception as e:
        return [{"error": str(e)}]
