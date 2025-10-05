"""Data models for the application."""

from app.models.schemas import (
    LocationRequest,
    EnvironmentalDataResponse,
    LocationInfo,
    PrecipitationData,
    AirQualityData,
    WeatherData,
    UVIndexData,
    FireHistoryData
)

__all__ = [
    "LocationRequest",
    "EnvironmentalDataResponse",
    "LocationInfo",
    "PrecipitationData",
    "AirQualityData",
    "WeatherData",
    "UVIndexData",
    "FireHistoryData"
]
