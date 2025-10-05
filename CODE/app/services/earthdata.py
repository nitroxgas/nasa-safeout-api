"""Service for interacting with NASA Earthdata using earthaccess."""

import logging
from typing import Optional, List, Any
from datetime import datetime, timedelta
import os

try:
    import earthaccess
except ImportError:
    earthaccess = None

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EarthdataService:
    """Service for accessing NASA Earthdata."""
    
    def __init__(self):
        """Initialize the Earthdata service."""
        self.authenticated = False
        self.auth = None
        
        if earthaccess is None:
            logger.error("earthaccess library not installed")
            return
        
        # Authenticate
        try:
            if settings.earthdata_username and settings.earthdata_password:
                self.auth = earthaccess.login(
                    strategy="environment",
                    persist=True
                )
                self.authenticated = True
                logger.info("Successfully authenticated with NASA Earthdata")
            else:
                logger.warning(
                    "NASA Earthdata credentials not configured. "
                    "Set EARTHDATA_USERNAME and EARTHDATA_PASSWORD in .env"
                )
        except Exception as e:
            logger.error(f"Failed to authenticate with NASA Earthdata: {e}")
    
    def search_data(
        self,
        short_name: str,
        bbox: tuple,
        temporal: tuple,
        count: int = 10
    ) -> List[Any]:
        """
        Search for data in NASA Earthdata.
        
        Args:
            short_name: Dataset short name (e.g., 'GPM_3IMERGHHE')
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            temporal: Temporal range (start_date, end_date)
            count: Maximum number of results
            
        Returns:
            List of granules
        """
        if not self.authenticated:
            logger.error("Not authenticated with NASA Earthdata")
            return []
        
        try:
            results = earthaccess.search_data(
                short_name=short_name,
                bounding_box=bbox,
                temporal=temporal,
                count=count
            )
            logger.info(f"Found {len(results)} granules for {short_name}")
            return results
        except Exception as e:
            logger.error(f"Error searching for {short_name}: {e}")
            return []
    
    def download_granules(
        self,
        granules: List[Any],
        download_dir: Optional[str] = None
    ) -> List[str]:
        """
        Download granules from NASA Earthdata.
        
        Args:
            granules: List of granules to download
            download_dir: Directory to download to
            
        Returns:
            List of downloaded file paths
        """
        if not self.authenticated:
            logger.error("Not authenticated with NASA Earthdata")
            return []
        
        if download_dir is None:
            download_dir = settings.cache_dir
        
        # Create download directory if it doesn't exist
        os.makedirs(download_dir, exist_ok=True)
        
        try:
            files = earthaccess.download(
                granules,
                download_dir
            )
            logger.info(f"Downloaded {len(files)} files to {download_dir}")
            return files
        except Exception as e:
            logger.error(f"Error downloading granules: {e}")
            return []
    
    def get_imerg_data(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        hours_back: int = 24
    ) -> Optional[List[str]]:
        """
        Get IMERG precipitation data.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Search radius in kilometers
            hours_back: How many hours back to search
            
        Returns:
            List of downloaded file paths or None
        """
        # Calculate bounding box
        lat_offset = radius_km / 111.0  # Approximate km per degree latitude
        lon_offset = radius_km / (111.0 * abs(latitude))  # Adjust for latitude
        
        bbox = (
            longitude - lon_offset,
            latitude - lat_offset,
            longitude + lon_offset,
            latitude + lat_offset
        )
        
        # Calculate temporal range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        temporal = (
            start_time.strftime("%Y-%m-%d"),
            end_time.strftime("%Y-%m-%d")
        )
        
        # Search for data
        granules = self.search_data(
            short_name="GPM_3IMERGHHE",
            bbox=bbox,
            temporal=temporal,
            count=10
        )
        
        if not granules:
            return None
        
        # Download granules
        files = self.download_granules(granules)
        return files if files else None
    
    def get_merra2_data(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        hours_back: int = 24
    ) -> Optional[List[str]]:
        """
        Get MERRA-2 weather data.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Search radius in kilometers
            hours_back: How many hours back to search
            
        Returns:
            List of downloaded file paths or None
        """
        # Calculate bounding box
        lat_offset = radius_km / 111.0
        lon_offset = radius_km / (111.0 * abs(latitude))
        
        bbox = (
            longitude - lon_offset,
            latitude - lat_offset,
            longitude + lon_offset,
            latitude + lat_offset
        )
        
        # Calculate temporal range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        temporal = (
            start_time.strftime("%Y-%m-%d"),
            end_time.strftime("%Y-%m-%d")
        )
        
        # Search for data
        granules = self.search_data(
            short_name="M2I1NXASM",
            bbox=bbox,
            temporal=temporal,
            count=10
        )
        
        if not granules:
            return None
        
        # Download granules
        files = self.download_granules(granules)
        return files if files else None
    
    def get_tropomi_data(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        days_back: int = 7
    ) -> Optional[List[str]]:
        """
        Get TROPOMI air quality data.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Search radius in kilometers
            days_back: How many days back to search
            
        Returns:
            List of downloaded file paths or None
        """
        # Calculate bounding box
        lat_offset = radius_km / 111.0
        lon_offset = radius_km / (111.0 * abs(latitude))
        
        bbox = (
            longitude - lon_offset,
            latitude - lat_offset,
            longitude + lon_offset,
            latitude + lat_offset
        )
        
        # Calculate temporal range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days_back)
        temporal = (
            start_time.strftime("%Y-%m-%d"),
            end_time.strftime("%Y-%m-%d")
        )
        
        # Search for aerosol index data
        granules = self.search_data(
            short_name="S5P_L2__AER_AI",
            bbox=bbox,
            temporal=temporal,
            count=10
        )
        
        if not granules:
            return None
        
        # Download granules
        files = self.download_granules(granules)
        return files if files else None
