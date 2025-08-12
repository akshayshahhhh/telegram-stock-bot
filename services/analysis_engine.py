# services/analysis_engine.py
import numpy as np
import pandas as pd
from utils.indicators import calculate_rsi, calculate_ema
from services.candle_patterns import detect_candlestick_pattern
from services.price_structure import detect_price_structure
from services.options_engine import get_option_chain
from services.corporate_engine import get_corporate_calendar  # new import

def analyze_stock(df: pd.DataFrame) -> dict:
    """
    Analyze stock DataFrame and return structured dict including:
      - CMP, RSI, EMAs
      - 52-Week High/Low & Percentile
      - Distance of CMP from each EMA
      - Dynamic 20-day Support/Resistance
      - Candlestick Patterns & Price Structure
      - Volume Analysis & Surge %
      - Breakout Setup
      - EMA Crossovers (21x50 & 50x200)
      - Option Chain: Max Call/Put OI & Max Pain Strike
      - Corporate & Events Calendar: Earnings, Ex-Dividend, Shareholding
    """
    try:
        # Validate & normalize input
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Invalid data format: Expected DataFrame")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(map(str, col)).strip() for col in df.columns]
        df.columns = [c.lower() for c in df.columns]
        required = {'open', 'high', 'low', 'close', 'volume'}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        # Indicators
        df['rsi_val'] = calculate_rsi(df['close'])
        df['ema_21']  = calculate_ema(df['close'], 21)
        df['ema_50']  = calculate_ema(df['close'], 50)
        df['ema_200'] = calculate_ema(df['close'], 200)

        # 52-Week Range & Percentile
        high_52w = round(df['high'].rolling(252, min_periods=1).max().iloc[-1], 2)
        low_52w  = round(df['low'].rolling(252, min_periods=1).min().iloc[-1], 2)

        # Snapshot
        latest     = df.iloc[-1]
        cmp_price  = round(float(latest['close']), 2)
        rsi_val    = round(float(latest['rsi_val']), 2)
        ema_21     = round(float(latest['ema_21']), 2)
        ema_50     = round(float(latest['ema_50']), 2)
        ema_200    = round(float(latest['ema_200']), 2)

        # 52-Week Percentile
        pct_52w = None
        if high_52w > low_52w:
            pct_52w = round((cmp_price - low_52w) / (high_52w - low_52w) * 100, 2)

        # EMA distances
        dist21  = round(abs(ema_21  - cmp_price) / cmp_price * 100, 2)
        dist50  = round(abs(ema_50  - cmp_price) / cmp_price * 100, 2)
        dist200 = round(abs(ema_200 - cmp_price) / cmp_price * 100, 2)

        # 20-Day Support & Resistance
        lows20   = df['low'].tail(20).astype(float)
        highs20  = df['high'].tail(20).astype(float)
        sup_low  = round(lows20.min(), 2)
        sup_high = round(lows20.mean(), 2)
        res_low  = round(highs20.mean(), 2)
        res_high = round(highs20.max(), 2)
        buf_low  = round(cmp_price * 0.97, 2)
        buf_res  = round(cmp_price * 1.03, 2)
        if sup_high >= cmp_price: sup_high = buf_low
        if sup_low  >= cmp_price: sup_low  = buf_low
        if res_low  <= cmp_price: res_low  = buf_res
        if res_high <= cmp_price: res_high = buf_res
        support_zone    = sorted([sup_low, sup_high])
        resistance_zone = sorted([res_low, res_high])

        # Candlestick Patterns & Price Structure
        daily_pattern  = detect_candlestick_pattern(
                            df[['open','high','low','close']].iloc[-2:]
                         )
        weekly_df      = df.resample('W').agg({
                            'open':'first','high':'max',
                            'low':'min','close':'last'
                         })
        weekly_pattern = (
            detect_candlestick_pattern(weekly_df[['open','high','low','close']].iloc[-2:])
            if len(weekly_df) >= 2 else "Not Enough Data"
        )
        daily_structure  = detect_price_structure(df[['high','low']].iloc[-5:])
        weekly_structure = (
            detect_price_structure(weekly_df[['high','low']].iloc[-5:])
            if len(weekly_df) >= 5 else "Not Enough Data"
        )

        # Volume Analysis
        vol_today        = int(latest['volume'])
        vol_avg50        = int(df['volume'].rolling(50).mean().iloc[-1])
        volume_signal    = "High Volume" if vol_today >= vol_avg50 else "Low Volume"
        vol_avg20        = df['volume'].rolling(20).mean().iloc[-1]
        volume_surge_pct = (
            round((vol_today - vol_avg20) / vol_avg20 * 100, 2)
            if pd.notna(vol_avg20) and vol_avg20 > 0 else None
        )

        # Breakout Setup
        swing_high_10   = float(df['high'].iloc[-10:].max())
        breakout_level  = round(swing_high_10 * 1.003, 2)
        breakout_volume = round((vol_avg50 * 1.2) / 100000, 2)

        # EMA Crossovers
        ema_21_50_cross  = 'None'
        ema_50_200_cross = 'None'
        if len(df) >= 2:
            prev, curr = df.iloc[-2], df.iloc[-1]
            if prev['ema_21'] < prev['ema_50'] and curr['ema_21'] > curr['ema_50']:
                ema_21_50_cross = 'Golden Cross (21x50)'
            elif prev['ema_21'] > prev['ema_50'] and curr['ema_21'] < curr['ema_50']:
                ema_21_50_cross = 'Death Cross (21x50)'
            if prev['ema_50'] < prev['ema_200'] and curr['ema_50'] > curr['ema_200']:
                ema_50_200_cross = 'Golden Cross (50x200)'
            elif prev['ema_50'] > prev['ema_200'] and curr['ema_50'] < curr['ema_200']:
                ema_50_200_cross = 'Death Cross (50x200)'

        # Option Chain: Max Call/Put OI & Max Pain Strike
        top_call_oi_strike   = None
        top_call_oi_interest = None
        top_put_oi_strike    = None
        top_put_oi_interest  = None
        max_pain_strike      = None
        try:
            opt_df = get_option_chain("TCS")
            if isinstance(opt_df, pd.DataFrame):
                opt_df.columns = [c.lower() for c in opt_df.columns]
                if {'strike','call_open_interest','put_open_interest'}.issubset(opt_df.columns):
                    calls = opt_df[['strike','call_open_interest']].dropna()
                    puts  = opt_df[['strike','put_open_interest']].dropna()
                    mc = calls.loc[calls['call_open_interest'].idxmax()]
                    mp = puts.loc[puts['put_open_interest'].idxmax()]
                    top_call_oi_strike   = round(float(mc['strike']), 2)
                    top_call_oi_interest = int(mc['call_open_interest'])
                    top_put_oi_strike    = round(float(mp['strike']), 2)
                    top_put_oi_interest  = int(mp['put_open_interest'])
                    opt_df['total_oi']   = (
                        opt_df['call_open_interest'] + opt_df['put_open_interest']
                    )
                    mpain = opt_df.loc[opt_df['total_oi'].idxmax()]
                    max_pain_strike = round(float(mpain['strike']), 2)
        except Exception:
            pass

        # Corporate & Events Calendar (New Section 6)
        corp = get_corporate_calendar("TCS")
        earnings_date        = corp.get('earnings_date', 'N/A')
        ex_dividend_date     = corp.get('ex_dividend_date', 'N/A')
        shareholding_changes = corp.get('shareholding_changes', 'N/A')

        return {
            'cmp': cmp_price,
            'rsi': rsi_val,
            'ema_21': ema_21,
            'ema_50': ema_50,
            'ema_200': ema_200,
            'dist21': dist21,
            'dist50': dist50,
            'dist200': dist200,
            'fifty_two_wk_high': high_52w,
            'fifty_two_wk_low': low_52w,
            'percentile_52w': pct_52w,
            'support_zone': support_zone,
            'resistance_zone': resistance_zone,
            'daily_pattern': daily_pattern,
            'weekly_pattern': weekly_pattern,
            'daily_structure': daily_structure,
            'weekly_structure': weekly_structure,
            'volume_today': round(vol_today/100000, 2),
            'volume_avg': round(vol_avg50/100000, 2),
            'volume_surge_pct': volume_surge_pct,
            'volume_signal': volume_signal,
            'breakout_level': breakout_level,
            'breakout_volume': breakout_volume,
            'ema_21_50_cross': ema_21_50_cross,
            'ema_50_200_cross': ema_50_200_cross,
            'top_call_oi_strike': top_call_oi_strike,
            'top_call_oi_interest': top_call_oi_interest,
            'top_put_oi_strike': top_put_oi_strike,
            'top_put_oi_interest': top_put_oi_interest,
            'max_pain_strike': max_pain_strike,
            'earnings_date': earnings_date,
            'ex_dividend_date': ex_dividend_date,
            'shareholding_changes': shareholding_changes
        }

    except Exception as e:
        import traceback; traceback.print_exc()
        return {'error': str(e)}
