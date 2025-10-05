"""Geospatial utility functions."""

import math
from typing import Tuple


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    
    Args:
        lat1: Latitude of point 1 in decimal degrees
        lon1: Longitude of point 1 in decimal degrees
        lat2: Latitude of point 2 in decimal degrees
        lon2: Longitude of point 2 in decimal degrees
        
    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers
    earth_radius_km = 6371.0
    
    return earth_radius_km * c


def calculate_bounding_box(
    latitude: float,
    longitude: float,
    radius_meters: int
) -> Tuple[float, float, float, float]:
    """
    Calculate a bounding box around a point.
    
    Args:
        latitude: Center latitude in decimal degrees
        longitude: Center longitude in decimal degrees
        radius_meters: Radius in meters
        
    Returns:
        Tuple of (min_lon, min_lat, max_lon, max_lat)
    """
    radius_km = radius_meters / 1000.0
    
    # Approximate degrees per kilometer
    # 1 degree latitude ≈ 111 km
    # 1 degree longitude ≈ 111 km * cos(latitude)
    lat_offset = radius_km / 111.0
    lon_offset = radius_km / (111.0 * abs(math.cos(math.radians(latitude))))
    
    min_lat = latitude - lat_offset
    max_lat = latitude + lat_offset
    min_lon = longitude - lon_offset
    max_lon = longitude + lon_offset
    
    # Ensure valid ranges
    min_lat = max(-90, min_lat)
    max_lat = min(90, max_lat)
    min_lon = max(-180, min_lon)
    max_lon = min(180, max_lon)
    
    return (min_lon, min_lat, max_lon, max_lat)


def wind_components_to_speed_direction(u: float, v: float) -> Tuple[float, float]:
    """
    Convert wind U and V components to speed and direction.
    
    Args:
        u: U component (east-west) in m/s
        v: V component (north-south) in m/s
        
    Returns:
        Tuple of (speed_m_s, direction_degrees)
        Direction is meteorological (direction wind is coming from)
    """
    # Calculate speed
    speed = math.sqrt(u ** 2 + v ** 2)
    
    # Calculate direction (mathematical angle)
    direction_rad = math.atan2(v, u)
    direction_deg = math.degrees(direction_rad)
    
    # Convert to meteorological direction (where wind is coming from)
    # Mathematical angle is where wind is going to
    meteorological_direction = (270 - direction_deg) % 360
    
    return speed, meteorological_direction


def direction_to_cardinal(degrees: float) -> str:
    """
    Convert wind direction in degrees to cardinal direction.
    
    Args:
        degrees: Direction in degrees (0-360)
        
    Returns:
        Cardinal direction string (N, NE, E, SE, S, SW, W, NW)
    """
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    index = round(degrees / 45) % 8
    return directions[index]


def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Convert temperature from Celsius to Fahrenheit.
    
    Args:
        celsius: Temperature in Celsius
        
    Returns:
        Temperature in Fahrenheit
    """
    return (celsius * 9/5) + 32


def kelvin_to_celsius(kelvin: float) -> float:
    """
    Convert temperature from Kelvin to Celsius.
    
    Args:
        kelvin: Temperature in Kelvin
        
    Returns:
        Temperature in Celsius
    """
    return kelvin - 273.15


def meters_per_second_to_kmh(mps: float) -> float:
    """
    Convert speed from meters per second to kilometers per hour.
    
    Args:
        mps: Speed in meters per second
        
    Returns:
        Speed in kilometers per hour
    """
    return mps * 3.6


def categorize_uv_index(uv_value: float) -> Tuple[str, str]:
    """
    Categorize UV index value.
    
    Args:
        uv_value: UV index value
        
    Returns:
        Tuple of (category, recommendation)
    """
    if uv_value < 3:
        return "low", "Baixo risco. Proteção mínima necessária."
    elif uv_value < 6:
        return "moderate", "Risco moderado. Use protetor solar."
    elif uv_value < 8:
        return "high", "Alto risco. Proteção necessária. Use protetor solar e evite exposição prolongada."
    elif uv_value < 11:
        return "very_high", "Risco muito alto. Proteção extra necessária. Evite exposição ao sol do meio-dia."
    else:
        return "extreme", "Risco extremo. Evite exposição ao sol. Tome todas as precauções."
