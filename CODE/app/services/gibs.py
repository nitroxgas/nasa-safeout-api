"""
NASA GIBS (Global Imagery Browse Services) integration.
Provides access to satellite imagery and visualization layers.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from owslib.wms import WebMapService
import requests

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GIBSService:
    """Service for accessing NASA GIBS imagery and data."""
    
    # GIBS WMS endpoints for different projections
    WMS_ENDPOINTS = {
        "epsg4326": "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi",
        "epsg3857": "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi",
        "epsg3413": "https://gibs.earthdata.nasa.gov/wms/epsg3413/best/wms.cgi",
        "epsg3031": "https://gibs.earthdata.nasa.gov/wms/epsg3031/best/wms.cgi",
    }
    
    # Useful layers for environmental data
    ENVIRONMENTAL_LAYERS = {
        "true_color": "MODIS_Terra_CorrectedReflectance_TrueColor",
        "aerosol": "MODIS_Combined_Value_Added_AOD",
        "cloud_top_temp": "AIRS_L2_Cloud_Top_Temperature_Day",
        "precipitation": "GPM_3IMERGHH_Precipitation_Rate",
        "land_surface_temp_day": "MODIS_Terra_Land_Surface_Temp_Day",
        "land_surface_temp_night": "MODIS_Terra_Land_Surface_Temp_Night",
        "fires": "MODIS_Terra_Thermal_Anomalies_All",
        "snow_cover": "MODIS_Terra_Snow_Cover",
        "vegetation": "MODIS_Terra_NDVI_8Day",
    }
    
    def __init__(self, projection: str = "epsg4326"):
        """
        Initialize GIBS service.
        
        Args:
            projection: Map projection (epsg4326, epsg3857, epsg3413, epsg3031)
        """
        self.projection = projection
        self.wms_url = self.WMS_ENDPOINTS.get(projection, self.WMS_ENDPOINTS["epsg4326"])
        self.wms = None
        
        try:
            self.wms = WebMapService(self.wms_url, version='1.1.1')
            logger.info(f"Connected to GIBS WMS: {self.wms_url}")
        except Exception as e:
            logger.error(f"Failed to connect to GIBS WMS: {e}")
    
    def get_available_layers(self) -> List[str]:
        """
        Get list of all available layers.
        
        Returns:
            List of layer names
        """
        if not self.wms:
            return []
        
        try:
            return list(self.wms.contents.keys())
        except Exception as e:
            logger.error(f"Error getting available layers: {e}")
            return []
    
    def get_layer_info(self, layer_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific layer.
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            Dictionary with layer information or None
        """
        if not self.wms:
            return None
        
        try:
            layer = self.wms[layer_name]
            return {
                "name": layer.name,
                "title": layer.title,
                "abstract": layer.abstract,
                "bbox": layer.boundingBoxWGS84,
                "styles": list(layer.styles.keys()) if layer.styles else [],
                "time_positions": layer.timepositions if hasattr(layer, 'timepositions') else None,
            }
        except Exception as e:
            logger.error(f"Error getting layer info for {layer_name}: {e}")
            return None
    
    def get_image_url(
        self,
        layer_name: str,
        bbox: tuple,
        width: int = 512,
        height: int = 512,
        date: Optional[str] = None,
        format: str = "image/png"
    ) -> Optional[str]:
        """
        Get URL for a GIBS image.
        
        Args:
            layer_name: Name of the layer
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            width: Image width in pixels
            height: Image height in pixels
            date: Date in YYYY-MM-DD format (default: today)
            format: Image format
            
        Returns:
            URL string or None
        """
        if not self.wms:
            return None
        
        if date is None:
            date = datetime.utcnow().strftime("%Y-%m-%d")
        
        try:
            # Build WMS GetMap request URL
            params = {
                "SERVICE": "WMS",
                "VERSION": "1.1.1",
                "REQUEST": "GetMap",
                "LAYERS": layer_name,
                "STYLES": "",
                "SRS": f"{self.projection.upper()}",
                "BBOX": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
                "WIDTH": str(width),
                "HEIGHT": str(height),
                "FORMAT": format,
                "TIME": date,
                "TRANSPARENT": "TRUE"
            }
            
            url = self.wms_url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
            return url
            
        except Exception as e:
            logger.error(f"Error generating image URL: {e}")
            return None
    
    def get_environmental_data(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get environmental data and imagery URLs for a location.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Radius around point in kilometers
            date: Date in YYYY-MM-DD format (default: today)
            
        Returns:
            Dictionary with imagery URLs and metadata
        """
        if date is None:
            date = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Calculate bounding box
        lat_offset = radius_km / 111.0
        lon_offset = radius_km / (111.0 * abs(max(abs(latitude), 0.1)))
        
        bbox = (
            longitude - lon_offset,
            latitude - lat_offset,
            longitude + lon_offset,
            latitude + lat_offset
        )
        
        result = {
            "source": "NASA GIBS",
            "date": date,
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "bbox": bbox
            },
            "imagery": {},
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # Generate URLs for key environmental layers
        for key, layer_name in self.ENVIRONMENTAL_LAYERS.items():
            try:
                url = self.get_image_url(layer_name, bbox, date=date)
                if url:
                    result["imagery"][key] = {
                        "layer": layer_name,
                        "url": url,
                        "description": self._get_layer_description(key)
                    }
            except Exception as e:
                logger.warning(f"Could not generate URL for {key}: {e}")
        
        return result
    
    def _get_layer_description(self, key: str) -> str:
        """Get human-readable description for a layer key."""
        descriptions = {
            "true_color": "True color satellite imagery",
            "aerosol": "Aerosol Optical Depth (air quality indicator)",
            "cloud_top_temp": "Cloud top temperature",
            "precipitation": "Precipitation rate",
            "land_surface_temp_day": "Land surface temperature (day)",
            "land_surface_temp_night": "Land surface temperature (night)",
            "fires": "Thermal anomalies and fires",
            "snow_cover": "Snow cover extent",
            "vegetation": "Vegetation index (NDVI)",
        }
        return descriptions.get(key, "")
    
    def get_fire_imagery(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 50.0,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get fire/thermal anomaly imagery for recent days.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Radius around point in kilometers
            days_back: Number of days to look back
            
        Returns:
            List of dictionaries with fire imagery data
        """
        # Calculate bounding box
        lat_offset = radius_km / 111.0
        lon_offset = radius_km / (111.0 * abs(max(abs(latitude), 0.1)))
        
        bbox = (
            longitude - lon_offset,
            latitude - lat_offset,
            longitude + lon_offset,
            latitude + lat_offset
        )
        
        results = []
        end_date = datetime.utcnow()
        
        for i in range(days_back):
            date = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
            
            try:
                url = self.get_image_url(
                    self.ENVIRONMENTAL_LAYERS["fires"],
                    bbox,
                    date=date
                )
                
                if url:
                    results.append({
                        "date": date,
                        "url": url,
                        "layer": self.ENVIRONMENTAL_LAYERS["fires"],
                        "description": "Thermal anomalies and active fires"
                    })
            except Exception as e:
                logger.warning(f"Could not generate fire imagery for {date}: {e}")
        
        return results
    
    def get_precipitation_imagery(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 50.0,
        hours_back: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get precipitation imagery for recent hours.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Radius around point in kilometers
            hours_back: Number of hours to look back
            
        Returns:
            List of dictionaries with precipitation imagery data
        """
        # Calculate bounding box
        lat_offset = radius_km / 111.0
        lon_offset = radius_km / (111.0 * abs(max(abs(latitude), 0.1)))
        
        bbox = (
            longitude - lon_offset,
            latitude - lat_offset,
            longitude + lon_offset,
            latitude + lat_offset
        )
        
        results = []
        end_time = datetime.utcnow()
        
        # GIBS precipitation is typically available every 30 minutes
        for i in range(0, hours_back, 1):  # Check every hour
            time = end_time - timedelta(hours=i)
            date_str = time.strftime("%Y-%m-%dT%H:00:00Z")
            
            try:
                url = self.get_image_url(
                    self.ENVIRONMENTAL_LAYERS["precipitation"],
                    bbox,
                    date=date_str
                )
                
                if url:
                    results.append({
                        "time": date_str,
                        "url": url,
                        "layer": self.ENVIRONMENTAL_LAYERS["precipitation"],
                        "description": "Precipitation rate (mm/hr)"
                    })
            except Exception as e:
                logger.warning(f"Could not generate precipitation imagery for {date_str}: {e}")
        
        return results
