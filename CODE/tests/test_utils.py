"""Tests for utility functions."""

import pytest
import math
from app.utils.geo_utils import (
    haversine_distance,
    calculate_bounding_box,
    wind_components_to_speed_direction,
    direction_to_cardinal,
    celsius_to_fahrenheit,
    kelvin_to_celsius,
    meters_per_second_to_kmh,
    categorize_uv_index
)


def test_haversine_distance():
    """Test haversine distance calculation."""
    # Distance between New York and London (approximately 5570 km)
    ny_lat, ny_lon = 40.7128, -74.0060
    london_lat, london_lon = 51.5074, -0.1278
    
    distance = haversine_distance(ny_lat, ny_lon, london_lat, london_lon)
    
    # Should be approximately 5570 km (allow 10% margin)
    assert 5000 < distance < 6000


def test_haversine_distance_same_point():
    """Test haversine distance for same point."""
    distance = haversine_distance(0, 0, 0, 0)
    assert distance == 0


def test_calculate_bounding_box():
    """Test bounding box calculation."""
    lat, lon = 0, 0
    radius = 10000  # 10 km
    
    min_lon, min_lat, max_lon, max_lat = calculate_bounding_box(lat, lon, radius)
    
    assert min_lat < lat < max_lat
    assert min_lon < lon < max_lon


def test_wind_components_to_speed_direction():
    """Test wind component conversion."""
    # East wind (u=10, v=0)
    speed, direction = wind_components_to_speed_direction(10, 0)
    assert speed == 10
    assert 265 < direction < 275  # Should be around 270 (from west)
    
    # North wind (u=0, v=10)
    speed, direction = wind_components_to_speed_direction(0, 10)
    assert speed == 10
    assert 175 < direction < 185  # Should be around 180 (from south)


def test_direction_to_cardinal():
    """Test cardinal direction conversion."""
    assert direction_to_cardinal(0) == "N"
    assert direction_to_cardinal(45) == "NE"
    assert direction_to_cardinal(90) == "E"
    assert direction_to_cardinal(135) == "SE"
    assert direction_to_cardinal(180) == "S"
    assert direction_to_cardinal(225) == "SW"
    assert direction_to_cardinal(270) == "W"
    assert direction_to_cardinal(315) == "NW"
    assert direction_to_cardinal(360) == "N"


def test_celsius_to_fahrenheit():
    """Test Celsius to Fahrenheit conversion."""
    assert celsius_to_fahrenheit(0) == 32
    assert celsius_to_fahrenheit(100) == 212
    assert abs(celsius_to_fahrenheit(20) - 68) < 0.1


def test_kelvin_to_celsius():
    """Test Kelvin to Celsius conversion."""
    assert kelvin_to_celsius(273.15) == 0
    assert abs(kelvin_to_celsius(373.15) - 100) < 0.1


def test_meters_per_second_to_kmh():
    """Test m/s to km/h conversion."""
    assert meters_per_second_to_kmh(1) == 3.6
    assert abs(meters_per_second_to_kmh(10) - 36) < 0.1


def test_categorize_uv_index():
    """Test UV index categorization."""
    category, _ = categorize_uv_index(1)
    assert category == "low"
    
    category, _ = categorize_uv_index(4)
    assert category == "moderate"
    
    category, _ = categorize_uv_index(7)
    assert category == "high"
    
    category, _ = categorize_uv_index(9)
    assert category == "very_high"
    
    category, _ = categorize_uv_index(12)
    assert category == "extreme"
