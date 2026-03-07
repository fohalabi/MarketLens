import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns correct app info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "MarketLens"
    assert data["status"] == "running"


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_commodities_list():
    """Test commodities list endpoint."""
    response = client.get("/api/commodities/")
    assert response.status_code == 200
    data = response.json()
    assert "commodities" in data
    assert len(data["commodities"]) > 0


def test_invalid_commodity():
    """Test that invalid commodity returns 400."""
    response = client.get("/api/commodities/INVALIDCOMMODITY")
    assert response.status_code == 400