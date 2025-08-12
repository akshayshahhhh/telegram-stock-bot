# services/structured_report.py
from datetime import datetime
from services.fundamental_engine import get_fundamentals, get_annual_fundamentals

def generate_structured_report(stock_name: str, analysis: dict) -> str:
    """
    Full technical + fundamental snapshot including:
      I.   Price Summary
      II.  Trend Overview
      III. Indicators
      IV.  Price Action
      V.   Volume Analysis
      VI.  Fundamental Snapshot
      VII. 3-Year Fundamental Trends (2023–2025)
    """
    # Error
    if 'error' in analysis:
        return f"⚠️ Error generating report for {stock_name.upper()}: {analysis['error']}"

    # Helpers
    label = lambda txt: txt.ljust(22)
    def fmt_cr(val):
        return f"₹{val/1e7:,.2f} Cr" if val is not None else "N/A"

    # Core
    date_str  = datetime.now().strftime("%Y-%m-%d")
    cmp_price = analysis.get('cmp', 0)
    low52     = analysis.get('fifty_two_wk_low')
    high52    = analysis.get('fifty_two_wk_high')

    # Build header
    report  = f"📘 {stock_name.upper()} – Technical Snapshot\n"
    report += f"Date: {date_str}\n\n"

    # I. Price Summary
    report += "🔹 I. Price Summary\n"
    report += f"  • {label('CMP (NSE)')}: ₹{cmp_price}\n"

    # Correct 52-Week Position relative to CMP
    pos_text = "N/A"
    if isinstance(cmp_price, (int, float)) and low52 and high52 and cmp_price > 0:
        low_dist  = (cmp_price - low52) / cmp_price * 100
        high_dist = (high52 - cmp_price) / cmp_price * 100
        if low_dist <= high_dist:
            pos_text = f"{low_dist:.2f}% Far From 52-Week Low"
        else:
            pos_text = f"{high_dist:.2f}% Far From 52-Week High"

    # Swapped order: Range first, then Position
    report += f"  • {label('52-Week Range')}: {low52} – {high52}\n"
    report += f"  • {label('52-Week Position')}: {pos_text}\n\n"

    # II. Trend Overview
    sup = analysis.get('support_zone', [])
    res = analysis.get('resistance_zone', [])
    trend = ("Strong Bullish"
             if isinstance(cmp_price, (int, float)) and cmp_price > analysis.get('ema_200', 0)
             else "Strong Bearish")
    report += "🔹 II. Trend Overview\n"
    report += f"  • {label('Trend')}: {trend}\n"
    report += f"  • {label('Support Zone')}: ₹{sup[0] if sup else 'N/A'} – ₹{sup[1] if len(sup)>1 else 'N/A'}\n"
    report += f"  • {label('Resistance Zone')}: ₹{res[0] if res else 'N/A'} – ₹{res[1] if len(res)>1 else 'N/A'}\n\n"

    # III. Indicators
    def fmt_dist(ema_key, dist_key):
        ema  = analysis.get(ema_key)
        dist = analysis.get(dist_key)
        if ema is None or dist is None:
            return "N/A"
        direction = "above" if ema > cmp_price else "below"
        return f"{abs(dist):.2f}% {direction}"

    report += "🔹 III. Indicators\n"
    report += f"  • {label('RSI (14)')}: {analysis.get('rsi','N/A')}\n"
    report += f"  • {label('EMA 21')}: ₹{analysis.get('ema_21','N/A')} ({fmt_dist('ema_21','dist21')})\n"
    report += f"  • {label('EMA 50')}: ₹{analysis.get('ema_50','N/A')} ({fmt_dist('ema_50','dist50')})\n"
    report += f"  • {label('EMA 200')}: ₹{analysis.get('ema_200','N/A')} ({fmt_dist('ema_200','dist200')})\n\n"

    # IV. Price Action
    report += "🔹 IV. Price Action\n"
    report += f"  • {label('Daily Pattern')}: {analysis.get('daily_pattern','N/A')}\n"
    report += f"  • {label('Daily Structure')}: {analysis.get('daily_structure','N/A')}\n"
    report += f"  • {label('Weekly Pattern')}: {analysis.get('weekly_pattern','N/A')}\n"
    report += f"  • {label('Weekly Structure')}: {analysis.get('weekly_structure','N/A')}\n\n"

    # V. Volume Analysis
    report += "🔹 V. Volume Analysis\n"
    report += f"  • {label('Today’s Volume')}: {analysis.get('volume_today','N/A')} Lakh\n"
    report += f"  • {label('Surge Over 20 Days')}: {analysis.get('volume_surge_pct','N/A')}%\n"
    report += f"  • {label('50-Day Avg Vol.')}: {analysis.get('volume_avg','N/A')} Lakh\n"
    report += f"  • {label('Volume Signal')}: {analysis.get('volume_signal','N/A')}\n\n"

    # VI. Fundamental Snapshot
    fund = get_fundamentals(stock_name)
    report += "🔹 VI. Fundamental Snapshot\n"
    report += f"  • {label('Market Cap')}: {fmt_cr(fund.get('market_cap'))}\n"
    report += f"  • {label('P/E (TTM)')}: {fund.get('trailing_pe',0):.2f}\n"
    report += f"  • {label('P/E (Forward)')}: {fund.get('forward_pe',0):.2f}\n"
    report += f"  • {label('P/B')}: {fund.get('price_to_book',0):.2f}\n"
    report += f"  • {label('Dividend Yield')}: {fund.get('dividend_yield',0)*100:.2f}%\n"
    report += f"  • {label('ROE')}: {fund.get('return_on_equity',0)*100:.2f}%\n"
    report += f"  • {label('Debt/Equity')}: {fund.get('debt_to_equity',0)/100:.2f}\n"
    report += f"  • {label('EPS (TTM)')}: {fund.get('eps_ttm',0):.2f}\n\n"

    # VII. 3-Year Fundamental Trends (2023–2025)
    af    = get_annual_fundamentals(stock_name)
    # sort and take last 4 years for YoY
    data = sorted(zip(af.get('years', []), af.get('revenue', []), af.get('pat', [])))
    report += "🔹 VII. 3-Year Fundamental Trends\n"
    header = " Year |  Revenue  | YoY Rev% |    PAT    | YoY PAT% \n"
    sep    = "-" * (len(header)-1) + "\n"
    report += header + sep

    if len(data) >= 4:
        last4 = data[-4:]
        # loop i=1→3 to get 2023,2024,2025 rows
        for i in range(1, 4):
            y0, r0, p0 = last4[i-1]
            y1, r1, p1 = last4[i]
            yoy_r = (r1 - r0) / r0 * 100 if r0 else 0
            yoy_p = (p1 - p0) / p0 * 100 if p0 else 0
            tag_r = f"🔺{yoy_r:.1f}%" if yoy_r >= 0 else f"🔻{abs(yoy_r):.1f}%"
            tag_p = f"🔺{yoy_p:.1f}%" if yoy_p >= 0 else f"🔻{abs(yoy_p):.1f}%"
            report += (
                f" {y1:<6}|  ₹{r1/1e7:,.0f} |   {tag_r} |   ₹{p1/1e7:,.0f} |   {tag_p}\n"
            )
    else:
        report += "  • N/A\n"

    # Disclaimer
    report += (
        "\n📌 Disclaimer: This analysis is for informational purposes only and "
        "should not be considered as investment advice. Please consult a qualified "
        "financial advisor before making any investment decisions. All investments "
        "involve risk, including the possible loss of principal. Past performance "
        "is not indicative of future results."
    )

    return report
