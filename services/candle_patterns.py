def detect_candlestick_pattern(df):
    try:
        if df.shape[0] < 2:
            return "Not Enough Data"

        prev = df.iloc[-2]
        curr = df.iloc[-1]

        def body(candle):
            return abs(candle['close'] - candle['open'])

        def is_bullish(candle):
            return candle['close'] > candle['open']

        def is_bearish(candle):
            return candle['open'] > candle['close']

        def upper_shadow(candle):
            return candle['high'] - max(candle['close'], candle['open'])

        def lower_shadow(candle):
            return min(candle['close'], candle['open']) - candle['low']

        curr_body = body(curr)
        prev_body = body(prev)
        curr_range = curr['high'] - curr['low']
        prev_range = prev['high'] - prev['low']

        # Avoid divide by zero
        if curr_range == 0 or prev_range == 0:
            return "Neutral"

        # --- Single Candle Patterns ---
        if curr_body / curr_range < 0.1:
            return "Doji"

        if curr_body / curr_range < 0.3 and upper_shadow(curr) > curr_body and lower_shadow(curr) > curr_body:
            return "Spinning Top"

        if lower_shadow(curr) > 2 * curr_body and upper_shadow(curr) < 0.3 * curr_body and is_bullish(curr):
            return "Hammer"

        if upper_shadow(curr) > 2 * curr_body and lower_shadow(curr) < 0.3 * curr_body and is_bearish(curr):
            return "Shooting Star"

        if is_bearish(curr) and lower_shadow(curr) > 2 * curr_body:
            return "Hanging Man"

        if is_bullish(curr) and upper_shadow(curr) > 2 * curr_body:
            return "Inverted Hammer"

        # --- Two Candle Patterns ---
        if is_bearish(curr) and is_bullish(prev):
            if curr['open'] > prev['close'] and curr['close'] < prev['open']:
                return "Bearish Engulfing"

        if is_bullish(curr) and is_bearish(prev):
            if curr['open'] < prev['close'] and curr['close'] > prev['open']:
                return "Bullish Engulfing"

        if is_bearish(curr) and is_bullish(prev):
            if curr['open'] > prev['close'] and curr['close'] < (prev['open'] + prev['close']) / 2:
                return "Dark Cloud Cover"

        if is_bullish(curr) and is_bearish(prev):
            if curr['close'] > (prev['open'] + prev['close']) / 2 and curr['open'] < prev['close']:
                return "Piercing Line"

        # Harami
        if is_bullish(prev) and is_bearish(curr):
            if curr['open'] < prev['close'] and curr['close'] > prev['open']:
                return "Bearish Harami"

        if is_bearish(prev) and is_bullish(curr):
            if curr['open'] > prev['close'] and curr['close'] < prev['open']:
                return "Bullish Harami"

        return "Neutral"

    except:
        return "Not Available"
