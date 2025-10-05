"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class LocationRequest(BaseModel):
    """Request model for location-based queries."""
    
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude in decimal degrees"
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude in decimal degrees"
    )
    radius_meters: int = Field(
        5000,
        ge=100,
        le=50000,
        description="Search radius in meters"
    )
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v


class LocationInfo(BaseModel):
    """Location information in the response."""
    
    latitude: float
    longitude: float
    radius_meters: int


class HourlyForecast(BaseModel):
    """Hourly precipitation forecast."""
    
    hour: int
    rate_mm_h: float
    confidence: str = "medium"


class PrecipitationData(BaseModel):
    """Precipitation data from IMERG."""
    
    source: str = "GPM_3IMERGHHE"
    last_update: Optional[str] = None
    forecast_hours: List[HourlyForecast] = []
    daily_accumulation_mm: Optional[float] = None


class SatelliteAirQuality(BaseModel):
    """Satellite-based air quality data."""
    
    source: str = "TROPOMI/Sentinel-5P"
    last_update: Optional[str] = None
    aerosol_index: Optional[float] = None
    no2_mol_m2: Optional[float] = None
    quality_flag: str = "unknown"


class Measurement(BaseModel):
    """Individual air quality measurement."""
    
    value: float
    unit: str
    aqi: str = "unknown"


class GroundStation(BaseModel):
    """Ground station air quality data."""
    
    location: str
    distance_km: float
    measurements: Dict[str, Measurement]
    last_update: str


class GroundAirQuality(BaseModel):
    """Ground-based air quality data from OpenAQ."""
    
    source: str = "OpenAQ"
    last_update: Optional[str] = None
    stations_count: int = 0
    stations: List[GroundStation] = []
    average: Optional[Dict[str, float]] = None


class AirQualityData(BaseModel):
    """Combined air quality data."""
    
    satellite: Optional[SatelliteAirQuality] = None
    ground_stations: Optional[GroundAirQuality] = None


class WindData(BaseModel):
    """Wind information."""
    
    speed_m_s: float
    speed_km_h: float
    direction_degrees: int
    direction_cardinal: str


class WeatherData(BaseModel):
    """Weather data from MERRA-2."""
    
    source: str = "MERRA-2"
    last_update: Optional[str] = None
    temperature_celsius: Optional[float] = None
    temperature_fahrenheit: Optional[float] = None
    humidity_percent: Optional[float] = None
    wind: Optional[WindData] = None
    pressure_hpa: Optional[float] = None


class UVIndexData(BaseModel):
    """UV index data."""
    
    source: str = "TROPOMI"
    last_update: Optional[str] = None
    value: Optional[float] = None
    category: str = "unknown"
    recommendation: str = ""


class FireEvent(BaseModel):
    """Individual fire detection event."""
    
    latitude: float
    longitude: float
    distance_km: float
    brightness_kelvin: float
    confidence: str
    confidence_percent: int
    date: str
    satellite: str


class FireHistoryData(BaseModel):
    """Fire detection history."""
    
    source: str = "NASA FIRMS"
    period_days: int = 7
    last_update: Optional[str] = None
    active_fires_count: int = 0
    fires: List[FireEvent] = []


class EnvironmentalData(BaseModel):
    """All environmental data combined."""
    
    precipitation: Optional[PrecipitationData] = None
    air_quality: Optional[AirQualityData] = None
    weather: Optional[WeatherData] = None
    uv_index: Optional[UVIndexData] = None
    fire_history: Optional[FireHistoryData] = None


class ResponseMetadata(BaseModel):
    """Response metadata."""
    
    processing_time_ms: int
    data_sources_queried: int
    data_sources_successful: int
    warnings: List[str] = []


class EnvironmentalDataResponse(BaseModel):
    """Complete response model."""
    
    location: LocationInfo
    timestamp: str
    data: EnvironmentalData
    metadata: ResponseMetadata


class APIInfo(BaseModel):
    """API information response."""
    
    name: str
    version: str
    description: str
    data_sources: List[Dict[str, str]]
    limits: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    timestamp: str
    services: Dict[str, str]
    version: str
