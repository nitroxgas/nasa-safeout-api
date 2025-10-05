"""Service for interacting with OpenAQ API."""

import logging
from typing import Optional, List, Dict, Any
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenAQService:
    """Service for accessing OpenAQ air quality data."""
    
    BASE_URL = "https://api.openaq.org/v2"
    
    def __init__(self):
        """Initialize the OpenAQ service."""
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def get_nearest_stations(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 25.0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get nearest air quality monitoring stations.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Search radius in kilometers
            limit: Maximum number of stations to return
            
        Returns:
            List of station data
        """
        try:
            params = {
                "coordinates": f"{latitude},{longitude}",
                "radius": int(radius_km * 1000),  # Convert to meters
                "limit": limit,
                "order_by": "distance"
            }
            
            response = await self.client.get(
                f"{self.BASE_URL}/locations",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            logger.info(f"Found {len(results)} stations near ({latitude}, {longitude})")
            return results
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching OpenAQ stations: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching OpenAQ stations: {e}")
            return []
    
    async def get_latest_measurements(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 25.0,
        parameters: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get latest measurements from nearby stations.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Search radius in kilometers
            parameters: List of parameters to fetch (e.g., ['pm25', 'pm10'])
            
        Returns:
            List of measurement data
        """
        if parameters is None:
            parameters = ["pm25", "pm10", "no2", "o3", "so2", "co"]
        
        try:
            params = {
                "coordinates": f"{latitude},{longitude}",
                "radius": int(radius_km * 1000),
                "limit": 100,
                "order_by": "distance"
            }
            
            response = await self.client.get(
                f"{self.BASE_URL}/latest",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            logger.info(f"Found {len(results)} measurements near ({latitude}, {longitude})")
            return results
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching OpenAQ measurements: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching OpenAQ measurements: {e}")
            return []
    
    def calculate_aqi(self, parameter: str, value: float) -> str:
        """
        Calculate Air Quality Index category for a parameter.
        
        Args:
            parameter: Parameter name (e.g., 'pm25', 'pm10')
            value: Measured value in µg/m³
            
        Returns:
            AQI category string
        """
        if parameter == "pm25":
            if value <= 12:
                return "good"
            elif value <= 35.4:
                return "moderate"
            elif value <= 55.4:
                return "unhealthy_sensitive"
            elif value <= 150.4:
                return "unhealthy"
            elif value <= 250.4:
                return "very_unhealthy"
            else:
                return "hazardous"
        
        elif parameter == "pm10":
            if value <= 54:
                return "good"
            elif value <= 154:
                return "moderate"
            elif value <= 254:
                return "unhealthy_sensitive"
            elif value <= 354:
                return "unhealthy"
            elif value <= 424:
                return "very_unhealthy"
            else:
                return "hazardous"
        
        elif parameter == "no2":
            if value <= 53:
                return "good"
            elif value <= 100:
                return "moderate"
            elif value <= 360:
                return "unhealthy_sensitive"
            elif value <= 649:
                return "unhealthy"
            elif value <= 1249:
                return "very_unhealthy"
            else:
                return "hazardous"
        
        elif parameter == "o3":
            if value <= 54:
                return "good"
            elif value <= 70:
                return "moderate"
            elif value <= 85:
                return "unhealthy_sensitive"
            elif value <= 105:
                return "unhealthy"
            elif value <= 200:
                return "very_unhealthy"
            else:
                return "hazardous"
        
        return "unknown"
    
    async def get_aggregated_data(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 25.0
    ) -> Dict[str, Any]:
        """
        Get aggregated air quality data from nearby stations.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Search radius in kilometers
            
        Returns:
            Aggregated air quality data
        """
        measurements = await self.get_latest_measurements(
            latitude, longitude, radius_km
        )
        
        if not measurements:
            return {}
        
        # Group measurements by location
        stations = {}
        for measurement in measurements:
            location_id = measurement.get("location")
            if location_id not in stations:
                stations[location_id] = {
                    "location": location_id,
                    "coordinates": measurement.get("coordinates", {}),
                    "measurements": {}
                }
            
            # Add measurement
            for m in measurement.get("measurements", []):
                param = m.get("parameter")
                value = m.get("value")
                unit = m.get("unit")
                
                if param and value is not None:
                    stations[location_id]["measurements"][param] = {
                        "value": value,
                        "unit": unit,
                        "aqi": self.calculate_aqi(param, value)
                    }
        
        return {
            "stations": list(stations.values()),
            "count": len(stations)
        }
