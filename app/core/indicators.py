import pandas as pd
import numpy as np
from typing import Dict, Any, List


def prepare_dataframe(data: List[dict]) -> pd.DataFrame:
    """
    Convert raw OHLCV list of dicts into a Pandas DataFrame.
    This is the first step before computing any indicator.
    """
    df = pd.DataFrame(data)
    df["close"] = pd.to_numeric(df["close"])
    df["open"] = pd.to_numeric(df["open"])
    df["high"] = pd.to_numeric(df["high"])
    df["low"] = pd.to_numeric(df["low"])
    df["volume"] = pd.to_numeric(df["volume"])
    return df


# MOVING AVERAGES 

def simple_moving_average(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    Simple Moving Average (SMA) — average price over N periods.
    Used to identify trend direction.
    """
    return df["close"].rolling(window=period).mean()


def exponential_moving_average(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    Exponential Moving Average (EMA) — like SMA but gives more
    weight to recent prices. Reacts faster to price changes.
    """
    return df["close"].ewm(span=period, adjust=False).mean()


# RSI 

def relative_strength_index(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Relative Strength Index (RSI) — measures overbought/oversold conditions.
    - RSI > 70 → overbought (price may drop soon)
    - RSI < 30 → oversold (price may rise soon)
    - Range: 0 to 100
    """
    delta = df["close"].diff()

    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Calculate average gain and loss over the period
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # RS = average gain / average loss
    rs = avg_gain / avg_loss

    # RSI formula
    rsi = 100 - (100 / (1 + rs))
    return rsi


# MACD 

def macd(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Dict[str, pd.Series]:
    """
    MACD — Moving Average Convergence Divergence.
    Shows momentum and trend direction changes.
    - MACD line crossing above signal → bullish (buy signal)
    - MACD line crossing below signal → bearish (sell signal)
    Returns: macd_line, signal_line, histogram
    """
    ema_fast = exponential_moving_average(df, fast_period)
    ema_slow = exponential_moving_average(df, slow_period)

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line

    return {
        "macd_line": macd_line,
        "signal_line": signal_line,
        "histogram": histogram
    }


# BOLLINGER BANDS 

def bollinger_bands(
    df: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2.0
) -> Dict[str, pd.Series]:
    """
    Bollinger Bands — volatility bands around a moving average.
    - Price near upper band → potentially overbought
    - Price near lower band → potentially oversold
    - Bands widening → increasing volatility
    - Bands narrowing → decreasing volatility (breakout incoming)
    Returns: upper_band, middle_band, lower_band
    """
    middle_band = simple_moving_average(df, period)
    std = df["close"].rolling(window=period).std()

    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)

    return {
        "upper_band": upper_band,
        "middle_band": middle_band,
        "lower_band": lower_band
    }


# VWAP

def vwap(df: pd.DataFrame) -> pd.Series:
    """
    Volume Weighted Average Price (VWAP).
    The average price weighted by volume — used as a benchmark
    by institutional traders for intraday trading.
    - Price above VWAP → bullish
    - Price below VWAP → bearish
    """
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    vwap_values = (typical_price * df["volume"]).cumsum() / df["volume"].cumsum()
    return vwap_values


# ATR 

def average_true_range(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Average True Range (ATR) — measures market volatility.
    Higher ATR = more volatile market.
    Used to set stop-loss levels in trading strategies.
    """
    high_low = df["high"] - df["low"]
    high_close = abs(df["high"] - df["close"].shift())
    low_close = abs(df["low"] - df["close"].shift())

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr


# RUN ALL INDICATORS 

def run_all_indicators(data: List[dict]) -> Dict[str, Any]:
    """
    Master function — runs all indicators on a dataset
    and returns a clean dictionary ready to store in the DB
    or send as an API response.
    """
    df = prepare_dataframe(data)

    # Get the last (most recent) value of each indicator
    # .iloc[-1] is like arr[arr.length - 1] in JavaScript
    sma_20 = simple_moving_average(df, 20)
    sma_50 = simple_moving_average(df, 50)
    ema_20 = exponential_moving_average(df, 20)
    rsi_14 = relative_strength_index(df, 14)
    macd_data = macd(df)
    bb_data = bollinger_bands(df)
    vwap_data = vwap(df)
    atr_data = average_true_range(df)

    def safe_float(series):
        """Safely get last value — returns None if NaN"""
        val = series.iloc[-1]
        return round(float(val), 4) if not np.isnan(val) else None

    return {
        "sma_20": safe_float(sma_20),
        "sma_50": safe_float(sma_50),
        "ema_20": safe_float(ema_20),
        "rsi": safe_float(rsi_14),
        "rsi_signal": (
            "overbought" if safe_float(rsi_14) and safe_float(rsi_14) > 70
            else "oversold" if safe_float(rsi_14) and safe_float(rsi_14) < 30
            else "neutral"
        ),
        "macd": {
            "macd_line": safe_float(macd_data["macd_line"]),
            "signal_line": safe_float(macd_data["signal_line"]),
            "histogram": safe_float(macd_data["histogram"]),
        },
        "bollinger_bands": {
            "upper": safe_float(bb_data["upper_band"]),
            "middle": safe_float(bb_data["middle_band"]),
            "lower": safe_float(bb_data["lower_band"]),
        },
        "vwap": safe_float(vwap_data),
        "atr": safe_float(atr_data),
    }