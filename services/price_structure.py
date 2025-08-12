def detect_price_structure(df):
    try:
        if df.shape[0] < 4:
            return "Not Enough Data"

        highs = df['high'].values[-4:]
        lows = df['low'].values[-4:]

        if highs[3] > highs[2] > highs[1] > highs[0] and lows[3] > lows[2] > lows[1] > lows[0]:
            return "Higher High – Higher Low"

        if highs[3] < highs[2] < highs[1] < highs[0] and lows[3] < lows[2] < lows[1] < lows[0]:
            return "Lower High – Lower Low"

        if highs[3] > highs[2] and lows[3] < lows[2]:
            return "Expansion"

        if highs[3] < highs[2] and lows[3] > lows[2]:
            return "Contraction"

        return "Mixed Trend"
    except:
        return "Not Available"
