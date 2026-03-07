import pytest
from app.core.indicators import (
    prepare_dataframe,
    simple_moving_average,
    relative_strength_index,
    run_all_indicators
)

# Sample OHLCV data for testing
SAMPLE_DATA = [
    {"date": f"2024-01-{i:02d}", "open": 150+i, "high": 155+i,
     "low": 148+i, "close": 152+i, "volume": 1000000+i}
    for i in range(1, 61)  # 60 data points
]


def test_prepare_dataframe():
    """Test that raw data converts to DataFrame correctly."""
    df = prepare_dataframe(SAMPLE_DATA)
    assert len(df) == 60
    assert "close" in df.columns
    assert "volume" in df.columns


def test_simple_moving_average():
    """Test SMA calculation."""
    df = prepare_dataframe(SAMPLE_DATA)
    sma = simple_moving_average(df, period=20)
    # First 19 values should be NaN, 20th onwards should have values
    assert sma.iloc[:19].isna().all()
    assert not sma.iloc[19:].isna().any()


def test_rsi_range():
    """Test RSI is always between 0 and 100."""
    df = prepare_dataframe(SAMPLE_DATA)
    rsi = relative_strength_index(df, period=14)
    valid_rsi = rsi.dropna()
    assert (valid_rsi >= 0).all()
    assert (valid_rsi <= 100).all()


def test_run_all_indicators():
    """Test that run_all_indicators returns all expected keys."""
    result = run_all_indicators(SAMPLE_DATA)
    assert "rsi" in result
    assert "macd" in result
    assert "bollinger_bands" in result
    assert "sma_20" in result
    assert "ema_20" in result
    assert "vwap" in result
    assert "atr" in result


def test_rsi_signal():
    """Test RSI signal categorization."""
    result = run_all_indicators(SAMPLE_DATA)
    assert result["rsi_signal"] in ["overbought", "oversold", "neutral"]