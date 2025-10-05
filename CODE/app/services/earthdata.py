"""Service for interacting with NASA Earthdata using earthaccess."""

import logging
from typing import Optional, List, Any, Dict
from datetime import datetime, timedelta
import os
from pathlib import Path

try:
    import earthaccess
except ImportError:
    earthaccess = None

from app.config import get_settings
from app.utils.netcdf_processor import NetCDFProcessor, HDF5Processor

logger = logging.getLogger(__name__)
settings = get_settings()


class EarthdataService:
    """Service for accessing NASA Earthdata."""
    
    def __init__(self):
        """Initialize the Earthdata service."""
        self.authenticated = False
        self.auth = None
        self.netcdf_processor = NetCDFProcessor()
        self.hdf5_processor = HDF5Processor()
        
        if earthaccess is None:
            logger.error("earthaccess library not installed")
            return
        
        # Authenticate with token only
        try:
            if settings.earthdata_token:
                logger.info("Authenticating with NASA Earthdata using token")
                
                # Set token in environment
                os.environ["EARTHDATA_TOKEN"] = settings.earthdata_token
                
                # Try to login - earthaccess may retry internally
                try:
                    self.auth = earthaccess.login(strategy="environment")
                    
                    if self.auth and hasattr(self.auth, 'authenticated') and self.auth.authenticated:
                        self.authenticated = True
                        logger.info("Successfully authenticated with NASA Earthdata using token")
                    else:
                        logger.error("Authentication failed - token may be invalid or expired")
                        logger.info("Generate a new token at: https://urs.earthdata.nasa.gov/profile")
                except Exception as auth_error:
                    logger.error(f"Authentication error: {auth_error}")
                    logger.info("Please verify your token at: https://urs.earthdata.nasa.gov/profile")
            else:
                logger.warning(
                    "NASA Earthdata token not configured. "
                    "Set EARTHDATA_TOKEN in .env file"
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
            
            # Convert to string paths if necessary
            file_paths = []
            for f in files:
                if isinstance(f, str):
                    file_paths.append(f)
                elif hasattr(f, '__str__'):
                    file_paths.append(str(f))
                else:
                    logger.warning(f"Unknown file type: {type(f)}")
            
            logger.info(f"Downloaded {len(file_paths)} files to {download_dir}")
            return file_paths
        except Exception as e:
            logger.error(f"Error downloading granules: {e}")
            return []
    
    def get_imerg_data(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        hours_back: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        Get IMERG precipitation data and process it.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Search radius in kilometers
            hours_back: How many hours back to search
            
        Returns:
            Dictionary with precipitation data or None
        """
        if not self.authenticated:
            logger.warning("Not authenticated with NASA Earthdata")
            return None
        
        try:
            # Calculate bounding box - use larger area to ensure granule coverage
            # NASA granules typically cover large areas
            lat_offset = max(radius_km / 111.0, 0.5)  # At least 0.5 degrees
            lon_offset = max(radius_km / (111.0 * abs(max(abs(latitude), 0.1))), 0.5)
            
            bbox = (
                longitude - lon_offset,
                latitude - lat_offset,
                longitude + lon_offset,
                latitude + lat_offset
            )
            
            # Calculate temporal range - search last 7 days for better coverage
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)
            temporal = (
                start_time.strftime("%Y-%m-%d"),
                end_time.strftime("%Y-%m-%d")
            )
            
            logger.info(f"Searching IMERG data for bbox={bbox}, temporal={temporal}")
            
            # Search for data
            granules = self.search_data(
                short_name="GPM_3IMERGHHE",
                bbox=bbox,
                temporal=temporal,
                count=5
            )
            
            if not granules:
                logger.warning("No IMERG granules found")
                return None
            
            # Download granules
            files = self.download_granules(granules)
            
            if not files:
                logger.warning("Failed to download IMERG granules")
                return None
            
            # Process the most recent file
            latest_file = files[-1]
            logger.info(f"Processing IMERG file: {latest_file}")
            
            # Verify file exists and has valid extension
            if not os.path.exists(latest_file):
                logger.error(f"Downloaded file does not exist: {latest_file}")
                return None
            
            if not latest_file.endswith(('.nc', '.nc4', '.hdf', '.h5', '.he5')):
                logger.warning(f"File may not be NetCDF/HDF5: {latest_file}")
            
            # Extract precipitation rate
            precip_rate = self.netcdf_processor.extract_point_value(
                latest_file,
                "precipitationCal",  # Calibrated precipitation
                latitude,
                longitude,
                method="nearest"
            )
            
            if precip_rate is None:
                # Try alternative variable names
                for var_name in ["precipitation", "precip", "HQprecipitation"]:
                    precip_rate = self.netcdf_processor.extract_point_value(
                        latest_file,
                        var_name,
                        latitude,
                        longitude,
                        method="nearest"
                    )
                    if precip_rate is not None:
                        break
            
            if precip_rate is None:
                logger.warning("Could not extract precipitation value")
                return None
            
            # Get dataset info for timestamp
            dataset_info = self.netcdf_processor.get_dataset_info(latest_file)
            
            result = {
                "precipitation_rate_mm_hr": round(float(precip_rate), 2),
                "source": "GPM IMERG",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "latitude": latitude,
                "longitude": longitude,
                "file_processed": Path(latest_file).name
            }
            
            logger.info(f"Successfully processed IMERG data: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing IMERG data: {e}", exc_info=True)
            return None
    
    def get_merra2_data(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        hours_back: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        Get MERRA-2 weather data and process it.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Search radius in kilometers
            hours_back: How many hours back to search
            
        Returns:
            Dictionary with weather data or None
        """
        if not self.authenticated:
            logger.warning("Not authenticated with NASA Earthdata")
            return None
        
        try:
            # Calculate bounding box - use larger area for MERRA-2 grid
            # MERRA-2 has 0.5° x 0.625° resolution
            lat_offset = max(radius_km / 111.0, 1.0)  # At least 1 degree
            lon_offset = max(radius_km / (111.0 * abs(max(abs(latitude), 0.1))), 1.0)
            
            bbox = (
                longitude - lon_offset,
                latitude - lat_offset,
                longitude + lon_offset,
                latitude + lat_offset
            )
            
            # Calculate temporal range - search last 3 days
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=3)
            temporal = (
                start_time.strftime("%Y-%m-%d"),
                end_time.strftime("%Y-%m-%d")
            )
            
            logger.info(f"Searching MERRA-2 data for bbox={bbox}, temporal={temporal}")
            
            # Search for data
            granules = self.search_data(
                short_name="M2I1NXASM",
                bbox=bbox,
                temporal=temporal,
                count=3
            )
            
            if not granules:
                logger.warning("No MERRA-2 granules found")
                return None
            
            # Download granules
            files = self.download_granules(granules)
            
            if not files:
                logger.warning("Failed to download MERRA-2 granules")
                return None
            
            # Process the most recent file
            latest_file = files[-1]
            logger.info(f"Processing MERRA-2 file: {latest_file}")
            
            # Verify file exists
            if not os.path.exists(latest_file):
                logger.error(f"Downloaded file does not exist: {latest_file}")
                return None
            
            # Extract multiple variables
            variables = {
                "T2M": None,      # Temperature at 2m
                "U2M": None,      # U wind component at 2m
                "V2M": None,      # V wind component at 2m
                "QV2M": None,     # Specific humidity at 2m
            }
            
            # Try NetCDF format first
            for var_name in variables.keys():
                value = self.netcdf_processor.extract_point_value(
                    latest_file,
                    var_name,
                    latitude,
                    longitude,
                    method="nearest"
                )
                if value is not None:
                    variables[var_name] = value
            
            # If NetCDF didn't work, try HDF5
            if all(v is None for v in variables.values()):
                for var_name in variables.keys():
                    value = self.hdf5_processor.extract_variable(
                        latest_file,
                        var_name,
                        latitude,
                        longitude
                    )
                    if value is not None:
                        variables[var_name] = value
            
            # Check if we got at least temperature
            if variables["T2M"] is None:
                logger.warning("Could not extract MERRA-2 temperature")
                return None
            
            # Calculate wind speed and direction if we have components
            wind_speed_ms = None
            wind_direction_deg = None
            
            if variables["U2M"] is not None and variables["V2M"] is not None:
                import math
                u = variables["U2M"]
                v = variables["V2M"]
                wind_speed_ms = math.sqrt(u**2 + v**2)
                wind_direction_deg = (math.degrees(math.atan2(u, v)) + 180) % 360
            
            # Convert temperature from Kelvin to Celsius
            temp_celsius = variables["T2M"] - 273.15 if variables["T2M"] else None
            
            # Calculate relative humidity if we have specific humidity and temperature
            relative_humidity = None
            if variables["QV2M"] is not None and variables["T2M"] is not None:
                # Simplified calculation
                relative_humidity = min(100, variables["QV2M"] * 1000)  # Rough approximation
            
            result = {
                "temperature_celsius": round(temp_celsius, 2) if temp_celsius else None,
                "temperature_kelvin": round(variables["T2M"], 2) if variables["T2M"] else None,
                "wind_speed_ms": round(wind_speed_ms, 2) if wind_speed_ms else None,
                "wind_speed_kmh": round(wind_speed_ms * 3.6, 2) if wind_speed_ms else None,
                "wind_direction_deg": round(wind_direction_deg, 2) if wind_direction_deg else None,
                "humidity_percent": round(relative_humidity, 2) if relative_humidity else None,
                "pressure_pa": round(variables["PS"], 2) if variables["PS"] else None,
                "source": "MERRA-2",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "latitude": latitude,
                "longitude": longitude,
                "file_processed": Path(latest_file).name
            }
            
            logger.info(f"Successfully processed MERRA-2 data: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing MERRA-2 data: {e}", exc_info=True)
            return None
    
    def get_tropomi_data(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        days_back: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Get TROPOMI air quality data and process it.
        
        NOTE: TROPOMI/Sentinel-5P data is from ESA (Copernicus), not NASA Earthdata.
        This function is currently disabled as it requires separate ESA/Copernicus credentials.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Search radius in kilometers
            days_back: How many days back to search
            
        Returns:
            None (TROPOMI not available via NASA Earthdata)
        """
        logger.info("TROPOMI data is not available via NASA Earthdata (requires ESA/Copernicus access)")
        return None
    
    def get_uv_index_data(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate UV index from TROPOMI aerosol data.
        
        NOTE: UV Index calculation depends on TROPOMI data which is not available
        via NASA Earthdata (requires ESA/Copernicus access).
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Search radius in kilometers
            
        Returns:
            None (depends on TROPOMI which is unavailable)
        """
        logger.info("UV Index calculation unavailable (depends on TROPOMI/ESA data)")
        return None
