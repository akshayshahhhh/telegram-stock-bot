from datetime import datetime
from services.fundamental_engine import get_fundamentals



def generate_structured_report(stock_name: str, analysis: dict) -> str:
    """
    Generates a structured technical snapshot report for a stock, including dynamic 20-day
    support/resistance.

    Args:
        stock_name (str): The ticker or name of the stock.
        analysis (dict): The output from analyze_stock(), containing keys like 'cmp', 'rsi', 'ema_21', etc.

    Returns:
        str: A formatted multi-line report string.
    """
    # Handle analysis errors
    if 'error' in analysis:
        return f"⚠️ Error generating report for {stock_name.upper()}: {analysis['error']}"

    # Current date
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Trend determination
    trend = 'Strong Bullish' if analysis.get('cmp', 0) > analysis.get('ema_200', 0) else 'Strong Bearish'

    # Support Zone (dynamic 20-day)
    sup = analysis.get('support_zone', [])
    if isinstance(sup, (list, tuple)) and len(sup) == 2:
        support_text = f"₹{sup[0]} – ₹{sup[1]}"
    else:
        support_text = 'N/A'

    # Resistance Zone (dynamic 20-day)
    res = analysis.get('resistance_zone', [])
    if isinstance(res, (list, tuple)) and len(res) == 2:
        resistance_text = f"₹{res[0]} – ₹{res[1]}"
    else:
        resistance_text = 'N/A'

    
    # Build structured report
    report = f"""📘 {stock_name.upper()} – Technical Snapshot
Date : {date_str}

🔹 I. Price Summary
• CMP (NSE) : ₹{analysis.get('cmp', 'N/A')}
• 52-Week Range : {analysis.get('fifty_two_wk_low', 'Not Available')} – {analysis.get('fifty_two_wk_high', 'Not Available')}

🔹 II. Trend Overview
• Trend : {trend}
• Support Zone : {support_text}
• Resistance Zone : {resistance_text}

🔹 III. Indicators
• RSI (14) : {analysis.get('rsi', 'N/A')}
• EMA 21 : ₹{analysis.get('ema_21', 'N/A')}
• EMA 50 : ₹{analysis.get('ema_50', 'N/A')}
• EMA 200 : ₹{analysis.get('ema_200', 'N/A')}

🔹 IV. Price Action
• Daily Candlestick Pattern : {analysis.get('daily_pattern', 'N/A')}
• Daily Structure : {analysis.get('daily_structure', 'N/A')}
• Weekly Candlestick Pattern : {analysis.get('weekly_pattern', 'N/A')}
• Weekly Structure : {analysis.get('weekly_structure', 'N/A')}

🔹 V. Volume Analysis
• Today’s Volume : {analysis.get('volume_today', 'N/A')} Lakh Shares
• 50 - Day Avg Volume : {analysis.get('volume_avg', 'N/A')} Lakh Shares
• Volume Signal : {analysis.get('volume_signal', 'N/A')}

🔹 VI. Breakout Setup
• Only if Price Crosses ₹{analysis.get('breakout_level', 'N/A')} with Strong Volume of ~ {analysis.get('breakout_volume', 'N/A')} Lakh Shares

📌 Disclaimer: This analysis is for informational purposes only and should not be considered as investment advice. Please consult a qualified financial advisor before making any investment decisions. All investments involve risk, including the possible loss of principal. Past performance is not indicative of future results.
"""
    return report
