"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_api_info():
    """Test API info endpoint."""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "data_sources" in data
    assert len(data["data_sources"]) > 0


def test_environmental_data_valid_request():
    """Test environmental data endpoint with valid request."""
    payload = {
        "latitude": -27.5954,
        "longitude": -48.5480,
        "radius_meters": 5000
    }
    response = client.post("/api/v1/environmental-data", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "location" in data
    assert "timestamp" in data
    assert "data" in data
    assert "metadata" in data


def test_environmental_data_invalid_latitude():
    """Test environmental data endpoint with invalid latitude."""
    payload = {
        "latitude": 100,  # Invalid
        "longitude": -48.5480,
        "radius_meters": 5000
    }
    response = client.post("/api/v1/environmental-data", json=payload)
    assert response.status_code == 422  # Validation error


def test_environmental_data_invalid_longitude():
    """Test environmental data endpoint with invalid longitude."""
    payload = {
        "latitude": -27.5954,
        "longitude": 200,  # Invalid
        "radius_meters": 5000
    }
    response = client.post("/api/v1/environmental-data", json=payload)
    assert response.status_code == 422  # Validation error


def test_environmental_data_invalid_radius():
    """Test environmental data endpoint with invalid radius."""
    payload = {
        "latitude": -27.5954,
        "longitude": -48.5480,
        "radius_meters": 100000  # Too large
    }
    response = client.post("/api/v1/environmental-data", json=payload)
    assert response.status_code == 422  # Validation error


def test_environmental_data_missing_fields():
    """Test environmental data endpoint with missing fields."""
    payload = {
        "latitude": -27.5954
        # Missing longitude
    }
    response = client.post("/api/v1/environmental-data", json=payload)
    assert response.status_code == 422  # Validation error


@pytest.mark.parametrize("lat,lon", [
    (0, 0),  # Equator, Prime Meridian
    (90, 0),  # North Pole
    (-90, 0),  # South Pole
    (0, 180),  # Date Line
    (0, -180),  # Date Line
])
def test_environmental_data_edge_cases(lat, lon):
    """Test environmental data endpoint with edge case coordinates."""
    payload = {
        "latitude": lat,
        "longitude": lon,
        "radius_meters": 5000
    }
    response = client.post("/api/v1/environmental-data", json=payload)
    assert response.status_code == 200
