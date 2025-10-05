"""Service for interacting with NASA FIRMS API."""

import logging
from typing import Optional, List, Dict, Any
import httpx
from datetime import datetime, timedelta

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class FIRMSService:
    """Service for accessing NASA FIRMS fire detection data."""
    
    BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api"
    
    def __init__(self):
        """Initialize the FIRMS service."""
        self.api_key = settings.firms_api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def get_active_fires(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 25.0,
        days_back: int = 7,
        source: str = "VIIRS_SNPP_NRT"
    ) -> List[Dict[str, Any]]:
        """
        Get active fire detections near a location.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Search radius in kilometers
            days_back: How many days back to search (1-10)
            source: Data source (VIIRS_SNPP_NRT, MODIS_NRT, etc.)
            
        Returns:
            List of fire detections
        """
        if not self.api_key:
            logger.warning("FIRMS API key not configured")
            return []
        
        # Limit days_back to valid range
        days_back = max(1, min(10, days_back))
        
        try:
            # FIRMS API endpoint for area search
            url = (
                f"{self.BASE_URL}/area/csv/"
                f"{self.api_key}/{source}/"
                f"{latitude},{longitude}/{radius_km}/{days_back}"
            )
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            # Parse CSV response
            fires = self._parse_csv_response(response.text)
            
            logger.info(
                f"Found {len(fires)} fire detections near "
                f"({latitude}, {longitude}) in last {days_back} days"
            )
            return fires
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching FIRMS data: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching FIRMS data: {e}")
            return []
    
    def _parse_csv_response(self, csv_text: str) -> List[Dict[str, Any]]:
        """
        Parse CSV response from FIRMS API.
        
        Args:
            csv_text: CSV text response
            
        Returns:
            List of fire detection dictionaries
        """
        fires = []
        lines = csv_text.strip().split('\n')
        
        if len(lines) < 2:
            return fires
        
        # Parse header
        header = lines[0].split(',')
        
        # Parse data rows
        for line in lines[1:]:
            values = line.split(',')
            if len(values) != len(header):
                continue
            
            fire = dict(zip(header, values))
            
            # Convert numeric fields
            try:
                fire['latitude'] = float(fire.get('latitude', 0))
                fire['longitude'] = float(fire.get('longitude', 0))
                fire['brightness'] = float(fire.get('brightness', 0))
                fire['confidence'] = fire.get('confidence', 'unknown')
                fire['frp'] = float(fire.get('frp', 0))  # Fire Radiative Power
            except (ValueError, KeyError):
                continue
            
            fires.append(fire)
        
        return fires
    
    def categorize_confidence(self, confidence: Any) -> tuple:
        """
        Categorize confidence value.
        
        Args:
            confidence: Confidence value (can be string or numeric)
            
        Returns:
            Tuple of (category_string, confidence_percent)
        """
        if isinstance(confidence, str):
            confidence_lower = confidence.lower()
            if confidence_lower in ['high', 'h']:
                return 'high', 85
            elif confidence_lower in ['nominal', 'n']:
                return 'medium', 65
            elif confidence_lower in ['low', 'l']:
                return 'low', 35
        
        try:
            conf_value = float(confidence)
            if conf_value >= 80:
                return 'high', int(conf_value)
            elif conf_value >= 50:
                return 'medium', int(conf_value)
            else:
                return 'low', int(conf_value)
        except (ValueError, TypeError):
            pass
        
        return 'unknown', 0
    
    async def get_fires_multiple_sources(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 25.0,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Get fire detections from multiple satellite sources.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Search radius in kilometers
            days_back: How many days back to search
            
        Returns:
            Combined fire detection data
        """
        sources = [
            "VIIRS_SNPP_NRT",  # VIIRS on Suomi NPP
            "MODIS_NRT"        # MODIS on Terra and Aqua
        ]
        
        all_fires = []
        
        for source in sources:
            fires = await self.get_active_fires(
                latitude, longitude, radius_km, days_back, source
            )
            
            # Add source information
            for fire in fires:
                fire['satellite_source'] = source
            
            all_fires.extend(fires)
        
        # Remove duplicates (fires detected by multiple satellites)
        unique_fires = self._deduplicate_fires(all_fires)
        
        return {
            "fires": unique_fires,
            "count": len(unique_fires),
            "period_days": days_back,
            "sources": sources
        }
    
    def _deduplicate_fires(
        self,
        fires: List[Dict[str, Any]],
        distance_threshold_km: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate fire detections.
        
        Args:
            fires: List of fire detections
            distance_threshold_km: Distance threshold for considering fires as duplicates
            
        Returns:
            Deduplicated list of fires
        """
        if not fires:
            return []
        
        unique_fires = []
        
        for fire in fires:
            is_duplicate = False
            
            for unique_fire in unique_fires:
                # Calculate approximate distance
                lat_diff = abs(fire['latitude'] - unique_fire['latitude'])
                lon_diff = abs(fire['longitude'] - unique_fire['longitude'])
                
                # Rough distance in km (1 degree ≈ 111 km)
                distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111
                
                if distance < distance_threshold_km:
                    is_duplicate = True
                    # Keep the one with higher confidence
                    if fire.get('brightness', 0) > unique_fire.get('brightness', 0):
                        unique_fires.remove(unique_fire)
                        unique_fires.append(fire)
                    break
            
            if not is_duplicate:
                unique_fires.append(fire)
        
        return unique_fires
