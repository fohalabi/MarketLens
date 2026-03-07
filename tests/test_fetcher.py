import pytest
from app.core.fetcher import fetch_stock, fetch_stock_history


def test_fetch_stock_returns_expected_keys():
    """Test that fetch_stock returns all expected fields."""
    data = fetch_stock("AAPL")
    assert "symbol" in data
    assert "name" in data
    assert "current_price" in data
    assert data["symbol"] == "AAPL"


def test_fetch_stock_invalid_symbol():
    """Test that invalid symbol returns None for current_price."""
    data = fetch_stock("INVALIDXYZ123")
    assert data["current_price"] is None


def test_fetch_stock_history_returns_data():
    """Test that history returns OHLCV data."""
    history = fetch_stock_history("AAPL", period="1mo")
    assert "data" in history
    assert len(history["data"]) > 0
    assert "close" in history["data"][0]
    assert "volume" in history["data"][0]


def test_fetch_stock_history_period():
    """Test that period parameter affects data length."""
    history_1mo = fetch_stock_history("AAPL", period="1mo")
    history_3mo = fetch_stock_history("AAPL", period="3mo")
    assert len(history_3mo["data"]) > len(history_1mo["data"])