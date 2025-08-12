import requests
from bs4 import BeautifulSoup

# Basic keyword-based sentiment tags
POSITIVE_KEYWORDS = ["growth", "profit", "expansion", "surge", "record", "beats", "upgrade"]
NEGATIVE_KEYWORDS = ["loss", "decline", "fall", "drop", "cut", "downgrade", "crash", "fraud"]

def classify_sentiment(text: str) -> str:
    text = text.lower()
    if any(word in text for word in POSITIVE_KEYWORDS):
        return "✅ Positive"
    elif any(word in text for word in NEGATIVE_KEYWORDS):
        return "⚠️ Negative"
    else:
        return "ℹ️ Neutral"

def get_news_sentiment(stock_name: str, max_headlines: int = 5):
    try:
        query = stock_name + " stock"
        url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}"

        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, features="xml")
        items = soup.findAll("item")[:max_headlines]

        headlines = []
        for item in items:
            title = item.title.text
            sentiment = classify_sentiment(title)
            headlines.append(f"• {title} – {sentiment}")

        return headlines

    except Exception as e:
        return [f"⚠️ Error fetching news: {e}"]
