"""Service for interacting with NASA Earthdata using earthaccess."""

import logging
from typing import Optional, List, Any, Dict
from datetime import datetime, timedelta
import os
import math
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
    """Service for accessing NASA Earthdata using earthaccess library."""
    
    # Class-level authentication state to prevent multiple attempts
    _auth_attempted = False
    _auth_successful = False
    _shared_auth = None
    _attempted_methods: set[str] = set()  # {"token", "env", "netrc"}
    _backoff_until: Optional[datetime] = None  # skip auth attempts until this time
    
    def __init__(self):
        """
        Initialize the Earthdata service.
        
        Authentication follows earthaccess best practices:
        1. Uses EARTHDATA_TOKEN environment variable if available
        2. Automatically handles authentication via earthaccess.login()
        3. No manual credential management needed
        4. Only attempts authentication once per application lifecycle
        """
        self.netcdf_processor = NetCDFProcessor()
        self.hdf5_processor = HDF5Processor()
        
        if earthaccess is None:
            logger.error("earthaccess library not installed. Install with: pip install earthaccess")
            self.authenticated = False
            self.auth = None
            return
        
        # Initialize instance view of shared auth state, do NOT authenticate here
        self.authenticated = bool(EarthdataService._auth_successful)
        self.auth = EarthdataService._shared_auth
        # Authentication is deferred to first use to avoid blocking requests unnecessarily
    
    def _choose_next_auth_method(self) -> Optional[str]:
        """Choose the next single auth method to attempt without causing multiple retries.

        Order of preference per application run: token -> env(user/pass) -> netrc.
        We try exactly one per instantiation and remember attempted methods.
        """
        # If already authenticated, nothing to do
        if EarthdataService._auth_successful:
            return None

        # Determine availability
        token_available = bool(settings.earthdata_token)
        env_user = os.environ.get("EARTHDATA_USERNAME") or settings.earthdata_username
        env_pass = os.environ.get("EARTHDATA_PASSWORD") or settings.earthdata_password
        env_available = bool(env_user and env_pass)
        netrc_available = any((Path.home() / name).exists() for name in (".netrc", "_netrc"))

        # Pick next not-yet-attempted
        if token_available and "token" not in EarthdataService._attempted_methods:
            return "token"
        if env_available and "env" not in EarthdataService._attempted_methods:
            return "env"
        if netrc_available and "netrc" not in EarthdataService._attempted_methods:
            return "netrc"
        return None

    def _authenticate_once(self, method: str):
        """Attempt exactly one authentication method and record the outcome."""
        EarthdataService._auth_attempted = True
        try:
            if method == "token":
                # Configure environment for token auth only
                os.environ["EARTHDATA_TOKEN"] = settings.earthdata_token
                os.environ.pop("EARTHDATA_USERNAME", None)
                os.environ.pop("EARTHDATA_PASSWORD", None)
                logger.info("🔑 Using EARTHDATA_TOKEN for authentication")
                logger.info("🔐 Attempting NASA Earthdata authentication (token, single attempt)...")
                self.auth = earthaccess.login(strategy="environment", persist=False)
            elif method == "env":
                # Ensure user/pass are in environment and remove token to force user/pass
                if settings.earthdata_username:
                    os.environ["EARTHDATA_USERNAME"] = settings.earthdata_username
                if settings.earthdata_password:
                    os.environ["EARTHDATA_PASSWORD"] = settings.earthdata_password
                os.environ.pop("EARTHDATA_TOKEN", None)
                logger.info("👤 Using EARTHDATA_USERNAME/PASSWORD for authentication")
                logger.info("🔐 Attempting NASA Earthdata authentication (user/pass, single attempt)...")
                self.auth = earthaccess.login(strategy="environment", persist=False)
            elif method == "netrc":
                logger.info("📄 Using .netrc for authentication")
                logger.info("🔐 Attempting NASA Earthdata authentication (.netrc, single attempt)...")
                self.auth = earthaccess.login(strategy="netrc", persist=False)
            else:
                logger.error(f"Unknown authentication method: {method}")
                self.auth = None

            # Mark this method as attempted
            EarthdataService._attempted_methods.add(method)

            # Evaluate result
            success = False
            if self.auth and hasattr(self.auth, "authenticated"):
                success = bool(self.auth.authenticated)
            elif self.auth:
                success = True

            self.authenticated = success
            EarthdataService._auth_successful = success
            EarthdataService._shared_auth = self.auth if success else None

            if success:
                logger.info("✅ Successfully authenticated with NASA Earthdata")
            else:
                logger.error("❌ Authentication failed for method '%s'", method)
                logger.warning("⚠️ Not retrying other methods in the same request to prevent lockout")
                self._log_auth_help()
                # Set short backoff to avoid repeated attempts causing lockout (2 minutes)
                EarthdataService._backoff_until = datetime.utcnow() + timedelta(minutes=2)
        except Exception as e:
            EarthdataService._attempted_methods.add(method)
            logger.error(f"❌ Authentication error using method '{method}': {e}")
            logger.warning("⚠️ Not retrying other methods in the same request to prevent lockout")
            self._log_auth_help()
            self.authenticated = False
            EarthdataService._auth_successful = False
            EarthdataService._shared_auth = None
            msg = str(e).lower()
            if "locked" in msg or "invalid_account_status" in msg:
                EarthdataService._backoff_until = datetime.utcnow() + timedelta(minutes=10)
            else:
                EarthdataService._backoff_until = datetime.utcnow() + timedelta(minutes=2)
        
    @classmethod
    def reset_authentication(cls):
        """
        Reset authentication state.
        
        This allows a new authentication attempt after a failure.
        Use with caution - only call this after fixing credentials.
        """
        logger.info("🔄 Resetting NASA Earthdata authentication state")
        cls._auth_attempted = False
        cls._auth_successful = False
        cls._shared_auth = None
        cls._attempted_methods = set()
        cls._backoff_until = None

    def ensure_authenticated(self) -> bool:
        """Ensure there is an authenticated session, attempting at most one method now.

        Returns True if authenticated, False otherwise (without blocking with multiple retries).
        """
        # Already authenticated globally
        if EarthdataService._auth_successful:
            self.authenticated = True
            self.auth = EarthdataService._shared_auth
            return True

        # Respect backoff window
        if EarthdataService._backoff_until and datetime.utcnow() < EarthdataService._backoff_until:
            wait_s = int((EarthdataService._backoff_until - datetime.utcnow()).total_seconds())
            logger.warning(f"⏳ Skipping authentication due to backoff window ({wait_s}s remaining)")
            self.authenticated = False
            return False

        # Pick and attempt exactly one method
        method = self._choose_next_auth_method()
        if not method:
            # No methods left to try this run
            self.authenticated = False
            return False
        self._authenticate_once(method)
        return bool(self.authenticated)
    
    def _log_auth_help(self):
        """Log helpful information for authentication issues."""
        logger.info("=" * 60)
        logger.info("NASA Earthdata Authentication Help")
        logger.info("=" * 60)
        logger.info("To authenticate, you need to:")
        logger.info("1. Create an account at: https://urs.earthdata.nasa.gov/")
        logger.info("2. Generate a token at: https://urs.earthdata.nasa.gov/profile")
        logger.info("3. Add to .env file: EARTHDATA_TOKEN=your_token_here")
        logger.info("4. Authorize applications:")
        logger.info("   - Go to: https://urs.earthdata.nasa.gov/profile")
        logger.info("   - Click: Applications → Authorized Apps")
        logger.info("   - Approve: NASA GESDISC DATA ARCHIVE")
        logger.info("5. Restart the API to retry authentication")
        logger.info("=" * 60)
    
    def search_data(
        self,
        short_name: str,
        bbox: Optional[tuple] = None,
        temporal: Optional[tuple] = None,
        count: int = 10,
        circle: Optional[tuple] = None,
        provider: Optional[str] = None,
        downloadable: Optional[bool] = True,
        cloud_hosted: Optional[bool] = None,
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
        if not self.ensure_authenticated():
            logger.warning("Not authenticated with NASA Earthdata (skipping search)")
            return []
        
        try:
            # Build kwargs according to earthaccess.search_data()
            kwargs: Dict[str, Any] = {
                "short_name": short_name,
            }
            if temporal:
                kwargs["temporal"] = temporal
            if bbox:
                kwargs["bounding_box"] = bbox
            if circle:
                # circle format: (lon, lat, radius_m)
                kwargs["circle"] = circle
            if provider:
                kwargs["provider"] = provider
            if downloadable is not None:
                kwargs["downloadable"] = downloadable
            if cloud_hosted is not None:
                kwargs["cloud_hosted"] = cloud_hosted

            results = earthaccess.search_data(
                count=count,
                **kwargs
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
        Download granules from NASA Earthdata using earthaccess.
        
        Args:
            granules: List of granules from earthaccess.search_data()
            download_dir: Directory to download to (default: cache_dir)
            
        Returns:
            List of downloaded file paths as strings
        """
        if not self.ensure_authenticated():
            logger.warning("❌ Not authenticated with NASA Earthdata (skipping download)")
            return []
        
        if not granules:
            logger.warning("No granules provided for download")
            return []
        
        if download_dir is None:
            download_dir = settings.cache_dir
        
        # Create download directory if it doesn't exist
        os.makedirs(download_dir, exist_ok=True)
        
        try:
            logger.info(f"Downloading {len(granules)} granule(s) to {download_dir}")
            
            # earthaccess.download() returns a list of file paths
            # It handles authentication automatically using the auth object
            files = earthaccess.download(
                granules,
                local_path=download_dir
            )
            
            # Ensure we have string paths
            file_paths = []
            for f in files:
                if isinstance(f, (str, Path)):
                    file_paths.append(str(f))
                elif hasattr(f, '__fspath__'):
                    file_paths.append(os.fspath(f))
                else:
                    logger.warning(f"Unexpected file type: {type(f)}, value: {f}")
                    # Try to convert to string anyway
                    try:
                        file_paths.append(str(f))
                    except:
                        pass
            
            logger.info(f"✅ Successfully downloaded {len(file_paths)} file(s)")
            return file_paths
            
        except Exception as e:
            logger.error(f"❌ Error downloading granules: {e}")
            logger.info("Check your NASA Earthdata credentials and network connection")
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
        if not self.ensure_authenticated():
            logger.warning("Not authenticated with NASA Earthdata (skipping IMERG)")
            return None
        
        try:
            # Spatial filter: use circle as recommended by earthaccess
            radius_m = int(max(radius_km, 1.0) * 1000)
            circle = (longitude, latitude, radius_m)
            
            # Calculate temporal range - search last 7 days for better coverage
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)
            temporal = (
                start_time.strftime("%Y-%m-%d"),
                end_time.strftime("%Y-%m-%d")
            )
            
            logger.info(f"Searching IMERG data for circle={circle}, temporal={temporal}")
            
            # Search for data
            granules = self.search_data(
                short_name="GPM_3IMERGHHE",
                circle=circle,
                temporal=temporal,
                count=5,
                downloadable=True
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
            # Spatial filter: use circle around point
            radius_m = int(max(radius_km, 1.0) * 1000)
            circle = (longitude, latitude, radius_m)
            
            # Calculate temporal range - search last 3 days
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=3)
            temporal = (
                start_time.strftime("%Y-%m-%d"),
                end_time.strftime("%Y-%m-%d")
            )
            
            logger.info(f"Searching MERRA-2 data for circle={circle}, temporal={temporal}")
            
            # Search for data
            granules = self.search_data(
                short_name="M2I1NXASM",
                circle=circle,
                temporal=temporal,
                count=3,
                downloadable=True
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
                "PS": None,       # Surface pressure
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
