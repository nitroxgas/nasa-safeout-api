"""Main data processor that orchestrates data fetching from all sources."""

import logging
from typing import Optional, Tuple
from datetime import datetime

from app.models.schemas import (
    PrecipitationData,
    AirQualityData,
    WeatherData,
    UVIndexData,
    FireHistoryData,
    SatelliteAirQuality,
    GroundAirQuality,
    GroundStation,
    Measurement,
    WindData,
    FireEvent
)
from app.services.openaq import OpenAQService
from app.services.firms import FIRMSService
from app.services.earthdata import EarthdataService
from app.services.gibs import GIBSService
from app.utils.geo_utils import (
    haversine_distance,
    categorize_uv_index,
    celsius_to_fahrenheit,
    meters_per_second_to_kmh,
    wind_components_to_speed_direction,
    direction_to_cardinal
)

logger = logging.getLogger(__name__)


class DataProcessor:
    """Orchestrates data fetching and processing from multiple sources."""
    
    def __init__(self):
        """Initialize the data processor."""
        self.logger = logging.getLogger(__name__)
        self.openaq_service = OpenAQService()
        self.firms_service = FIRMSService()
        self.earthdata_service = EarthdataService()
        self.gibs_service = GIBSService()
    
    async def get_precipitation_data(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int
    ) -> Optional[PrecipitationData]:
        """
        Fetch precipitation data from GPM IMERG.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_meters: Search radius in meters
            
        Returns:
            PrecipitationData or None if unavailable
        """
        try:
            self.logger.info("Fetching precipitation data from IMERG")
            
            # Convert radius to km
            radius_km = radius_meters / 1000.0
            
            # Get IMERG data
            imerg_data = self.earthdata_service.get_imerg_data(
                latitude, longitude, radius_km, hours_back=24
            )
            
            if not imerg_data:
                return None
            
            # Convert to PrecipitationData schema
            return PrecipitationData(
                source="GPM IMERG",
                last_update=imerg_data.get("timestamp"),
                precipitation_rate_mm_hr=imerg_data.get("precipitation_rate_mm_hr"),
                forecast_hours=None,
                confidence="high"
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching precipitation data: {e}", exc_info=True)
            return None
    
    async def get_air_quality_data(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int
    ) -> Optional[AirQualityData]:
        """
        Fetch air quality data from TROPOMI and OpenAQ.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_meters: Search radius in meters
            
        Returns:
            AirQualityData or None if unavailable
        """
        try:
            self.logger.info("Fetching air quality data from OpenAQ")
            
            # Convert radius to km
            radius_km = radius_meters / 1000.0
            
            # Fetch data from OpenAQ
            measurements = await self.openaq_service.get_latest_measurements(
                latitude, longitude, radius_km
            )
            
            ground_stations = None
            if measurements:
                # Group by location
                stations_dict = {}
                for measurement in measurements:
                    location_id = measurement.get("location", "Unknown")
                    
                    if location_id not in stations_dict:
                        coords = measurement.get("coordinates", {})
                        lat = coords.get("latitude", latitude)
                        lon = coords.get("longitude", longitude)
                        
                        # Calculate distance
                        distance = haversine_distance(latitude, longitude, lat, lon)
                        
                        stations_dict[location_id] = {
                            "location": location_id,
                            "distance_km": round(distance, 2),
                            "measurements": {},
                            "last_update": measurement.get("date", {}).get("utc", "")
                        }
                    
                    # Add measurements
                    for m in measurement.get("measurements", []):
                        param = m.get("parameter")
                        value = m.get("value")
                        unit = m.get("unit")
                        
                        if param and value is not None:
                            aqi = self.openaq_service.calculate_aqi(param, value)
                            stations_dict[location_id]["measurements"][param] = Measurement(
                                value=value,
                                unit=unit,
                                aqi=aqi
                            )
                
                # Convert to list and sort by distance
                stations_list = sorted(
                    stations_dict.values(),
                    key=lambda x: x["distance_km"]
                )[:5]  # Top 5 nearest
                
                # Calculate averages
                all_pm25 = []
                all_pm10 = []
                all_no2 = []
                
                for station in stations_list:
                    if "pm25" in station["measurements"]:
                        all_pm25.append(station["measurements"]["pm25"].value)
                    if "pm10" in station["measurements"]:
                        all_pm10.append(station["measurements"]["pm10"].value)
                    if "no2" in station["measurements"]:
                        all_no2.append(station["measurements"]["no2"].value)
                
                average = {}
                if all_pm25:
                    average["pm25"] = round(sum(all_pm25) / len(all_pm25), 2)
                if all_pm10:
                    average["pm10"] = round(sum(all_pm10) / len(all_pm10), 2)
                if all_no2:
                    average["no2"] = round(sum(all_no2) / len(all_no2), 2)
                
                # Determine overall AQI
                overall_aqi = "good"
                if average.get("pm25", 0) > 35.4:
                    overall_aqi = "unhealthy_sensitive"
                elif average.get("pm25", 0) > 12:
                    overall_aqi = "moderate"
                
                if average:
                    average["overall_aqi"] = overall_aqi
                
                # Convert to GroundStation objects
                ground_stations_list = [
                    GroundStation(**station) for station in stations_list
                ]
                
                ground_stations = GroundAirQuality(
                    source="OpenAQ",
                    last_update=datetime.utcnow().isoformat() + "Z",
                    stations_count=len(ground_stations_list),
                    stations=ground_stations_list,
                    average=average if average else None
                )
            
            # Get satellite data from TROPOMI
            radius_km = radius_meters / 1000.0
            tropomi_data = self.earthdata_service.get_tropomi_data(
                latitude, longitude, radius_km, days_back=3
            )
            
            if tropomi_data:
                satellite = SatelliteAirQuality(
                    source=tropomi_data.get("source", "TROPOMI/Sentinel-5P"),
                    last_update=tropomi_data.get("timestamp"),
                    aerosol_index=tropomi_data.get("aerosol_index"),
                    no2_mol_m2=tropomi_data.get("no2_column_mol_m2"),
                    quality_flag=tropomi_data.get("quality_flag", "unknown")
                )
            else:
                satellite = SatelliteAirQuality(
                    source="TROPOMI/Sentinel-5P",
                    last_update=None,
                    aerosol_index=None,
                    no2_mol_m2=None,
                    quality_flag="unavailable"
                )
            
            return AirQualityData(
                satellite=satellite,
                ground_stations=ground_stations
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching air quality data: {e}", exc_info=True)
            return None
    
    async def get_weather_data(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int
    ) -> Optional[WeatherData]:
        """
        Fetch weather data from MERRA-2.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_meters: Search radius in meters
            
        Returns:
            WeatherData or None if unavailable
        """
        try:
            self.logger.info("Fetching weather data from MERRA-2")
            
            # Convert radius to km
            radius_km = radius_meters / 1000.0
            
            # Get MERRA-2 data
            merra2_data = self.earthdata_service.get_merra2_data(
                latitude, longitude, radius_km, hours_back=24
            )
            
            if not merra2_data:
                return None
            
            # Create wind data if available
            wind = None
            if merra2_data.get("wind_speed_ms") is not None:
                wind = WindData(
                    speed_ms=merra2_data.get("wind_speed_ms"),
                    speed_kmh=merra2_data.get("wind_speed_kmh"),
                    direction_degrees=merra2_data.get("wind_direction_deg"),
                    direction_cardinal=direction_to_cardinal(merra2_data.get("wind_direction_deg")) if merra2_data.get("wind_direction_deg") else None
                )
            
            # Convert to WeatherData schema
            return WeatherData(
                source="MERRA-2",
                last_update=merra2_data.get("timestamp"),
                temperature_celsius=merra2_data.get("temperature_celsius"),
                temperature_fahrenheit=celsius_to_fahrenheit(merra2_data.get("temperature_celsius")) if merra2_data.get("temperature_celsius") else None,
                humidity_percent=merra2_data.get("humidity_percent"),
                pressure_hpa=merra2_data.get("pressure_pa") / 100 if merra2_data.get("pressure_pa") else None,
                wind=wind
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching weather data: {e}", exc_info=True)
            return None
    
    async def get_uv_index_data(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int
    ) -> Optional[UVIndexData]:
        """
        Fetch UV index data from TROPOMI.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_meters: Search radius in meters
            
        Returns:
            UVIndexData or None if unavailable
        """
        try:
            self.logger.info("Fetching UV index data from TROPOMI")
            
            # Convert radius to km
            radius_km = radius_meters / 1000.0
            
            # Get UV index data
            uv_data = self.earthdata_service.get_uv_index_data(
                latitude, longitude, radius_km
            )
            
            if not uv_data:
                return None
            
            # Convert to UVIndexData schema
            return UVIndexData(
                source=uv_data.get("source", "TROPOMI"),
                last_update=uv_data.get("timestamp"),
                uv_index=uv_data.get("uv_index"),
                category=uv_data.get("category"),
                risk_level=uv_data.get("risk_level")
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching UV index data: {e}", exc_info=True)
            return None
    
    async def get_fire_history_data(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int
    ) -> Optional[FireHistoryData]:
        """
        Fetch fire detection data from NASA FIRMS.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_meters: Search radius in meters
            
        Returns:
            FireHistoryData or None if unavailable
        """
        try:
            self.logger.info("Fetching fire history data from FIRMS")
            
            # Convert radius to km
            radius_km = radius_meters / 1000.0
            
            # Fetch fires from multiple sources
            result = await self.firms_service.get_fires_multiple_sources(
                latitude, longitude, radius_km, days_back=7
            )
            
            if not result or not result.get("fires"):
                return FireHistoryData(
                    source="NASA FIRMS",
                    period_days=7,
                    last_update=datetime.utcnow().isoformat() + "Z",
                    active_fires_count=0,
                    fires=[]
                )
            
            # Convert to FireEvent objects
            fire_events = []
            for fire in result["fires"]:
                # Calculate distance
                fire_lat = fire.get("latitude", 0)
                fire_lon = fire.get("longitude", 0)
                distance = haversine_distance(latitude, longitude, fire_lat, fire_lon)
                
                # Categorize confidence
                confidence_cat, confidence_pct = self.firms_service.categorize_confidence(
                    fire.get("confidence", "unknown")
                )
                
                # Determine satellite
                satellite = "VIIRS" if "VIIRS" in fire.get("satellite_source", "") else "MODIS"
                
                fire_event = FireEvent(
                    latitude=fire_lat,
                    longitude=fire_lon,
                    distance_km=round(distance, 2),
                    brightness_kelvin=fire.get("brightness", 0),
                    confidence=confidence_cat,
                    confidence_percent=confidence_pct,
                    date=fire.get("acq_date", datetime.utcnow().strftime("%Y-%m-%d")),
                    satellite=satellite
                )
                fire_events.append(fire_event)
            
            # Sort by distance
            fire_events.sort(key=lambda x: x.distance_km)
            
            return FireHistoryData(
                source="NASA FIRMS",
                period_days=7,
                last_update=datetime.utcnow().isoformat() + "Z",
                active_fires_count=len(fire_events),
                fires=fire_events[:20]  # Limit to 20 closest
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching fire history data: {e}", exc_info=True)
            return None
    
    def get_gibs_imagery(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int
    ) -> Optional[dict]:
        """
        Get GIBS satellite imagery URLs for a location.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_meters: Radius around point in meters
            
        Returns:
            Dictionary with imagery URLs or None
        """
        try:
            self.logger.info(f"Fetching GIBS imagery for ({latitude}, {longitude})")
            
            radius_km = radius_meters / 1000.0
            
            # Get environmental imagery
            imagery_data = self.gibs_service.get_environmental_data(
                latitude,
                longitude,
                radius_km
            )
            
            if imagery_data:
                self.logger.info(f"Successfully fetched GIBS imagery: {len(imagery_data.get('imagery', {}))} layers")
                return imagery_data
            else:
                self.logger.warning("No GIBS imagery data available")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching GIBS imagery: {e}", exc_info=True)
            return None
    
    async def close(self):
        """Close all service connections."""
        try:
            await self.openaq_service.close()
            await self.firms_service.close()
        except Exception as e:
            self.logger.error(f"Error closing services: {e}")
