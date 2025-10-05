"""Utility module for processing NetCDF and HDF5 files from NASA datasets."""

import logging
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import numpy as np

try:
    import xarray as xr
    import netCDF4
    HAS_NETCDF = True
except ImportError:
    HAS_NETCDF = False
    xr = None
    netCDF4 = None

try:
    import h5py
    HAS_H5PY = True
except ImportError:
    HAS_H5PY = False
    h5py = None

logger = logging.getLogger(__name__)


class NetCDFProcessor:
    """Processor for NetCDF and HDF5 files."""
    
    def __init__(self):
        """Initialize the NetCDF processor."""
        if not HAS_NETCDF:
            logger.warning("xarray or netCDF4 not installed. NetCDF processing unavailable.")
        if not HAS_H5PY:
            logger.warning("h5py not installed. HDF5 processing unavailable.")
    
    def extract_point_value(
        self,
        file_path: str,
        variable_name: str,
        latitude: float,
        longitude: float,
        method: str = "nearest"
    ) -> Optional[float]:
        """
        Extract value at a specific point from a NetCDF file.
        
        Args:
            file_path: Path to the NetCDF file
            variable_name: Name of the variable to extract
            latitude: Target latitude
            longitude: Target longitude
            method: Interpolation method ('nearest', 'linear')
            
        Returns:
            Extracted value or None if error
        """
        if not HAS_NETCDF:
            logger.error("xarray not available")
            return None
        
        try:
            with xr.open_dataset(file_path) as ds:
                # Check if variable exists
                if variable_name not in ds.variables:
                    logger.error(f"Variable {variable_name} not found in dataset")
                    return None
                
                # Get the variable
                var = ds[variable_name]
                
                # Find latitude and longitude dimension names
                lat_names = ['lat', 'latitude', 'Latitude', 'y']
                lon_names = ['lon', 'longitude', 'Longitude', 'x']
                
                lat_dim = None
                lon_dim = None
                
                for name in lat_names:
                    if name in ds.dims or name in ds.coords:
                        lat_dim = name
                        break
                
                for name in lon_names:
                    if name in ds.dims or name in ds.coords:
                        lon_dim = name
                        break
                
                if not lat_dim or not lon_dim:
                    logger.error("Could not find latitude/longitude dimensions")
                    return None
                
                # Select the point
                if method == "nearest":
                    point = var.sel({lat_dim: latitude, lon_dim: longitude}, method="nearest")
                else:
                    point = var.interp({lat_dim: latitude, lon_dim: longitude}, method=method)
                
                # Extract the value
                value = float(point.values)
                
                # Check for fill values or NaN
                if np.isnan(value) or np.isinf(value):
                    return None
                
                return value
                
        except Exception as e:
            logger.error(f"Error extracting point value from {file_path}: {e}")
            return None
    
    def extract_area_average(
        self,
        file_path: str,
        variable_name: str,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0
    ) -> Optional[float]:
        """
        Extract average value over an area from a NetCDF file.
        
        Args:
            file_path: Path to the NetCDF file
            variable_name: Name of the variable to extract
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Radius in kilometers
            
        Returns:
            Average value or None if error
        """
        if not HAS_NETCDF:
            logger.error("xarray not available")
            return None
        
        try:
            with xr.open_dataset(file_path) as ds:
                # Check if variable exists
                if variable_name not in ds.variables:
                    logger.error(f"Variable {variable_name} not found in dataset")
                    return None
                
                # Get the variable
                var = ds[variable_name]
                
                # Find latitude and longitude dimension names
                lat_names = ['lat', 'latitude', 'Latitude', 'y']
                lon_names = ['lon', 'longitude', 'Longitude', 'x']
                
                lat_dim = None
                lon_dim = None
                
                for name in lat_names:
                    if name in ds.dims or name in ds.coords:
                        lat_dim = name
                        break
                
                for name in lon_names:
                    if name in ds.dims or name in ds.coords:
                        lon_dim = name
                        break
                
                if not lat_dim or not lon_dim:
                    logger.error("Could not find latitude/longitude dimensions")
                    return None
                
                # Calculate bounding box
                lat_offset = radius_km / 111.0  # Approximate km per degree
                lon_offset = radius_km / (111.0 * np.cos(np.radians(latitude)))
                
                lat_min = latitude - lat_offset
                lat_max = latitude + lat_offset
                lon_min = longitude - lon_offset
                lon_max = longitude + lon_offset
                
                # Select the area
                area = var.sel(
                    {lat_dim: slice(lat_min, lat_max), lon_dim: slice(lon_min, lon_max)}
                )
                
                # Calculate mean
                mean_value = float(area.mean().values)
                
                # Check for fill values or NaN
                if np.isnan(mean_value) or np.isinf(mean_value):
                    return None
                
                return mean_value
                
        except Exception as e:
            logger.error(f"Error extracting area average from {file_path}: {e}")
            return None
    
    def extract_multiple_variables(
        self,
        file_path: str,
        variable_names: List[str],
        latitude: float,
        longitude: float,
        method: str = "nearest"
    ) -> Dict[str, Optional[float]]:
        """
        Extract multiple variables at a point from a NetCDF file.
        
        Args:
            file_path: Path to the NetCDF file
            variable_names: List of variable names to extract
            latitude: Target latitude
            longitude: Target longitude
            method: Interpolation method
            
        Returns:
            Dictionary mapping variable names to values
        """
        results = {}
        
        for var_name in variable_names:
            value = self.extract_point_value(
                file_path, var_name, latitude, longitude, method
            )
            results[var_name] = value
        
        return results
    
    def get_dataset_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a NetCDF dataset.
        
        Args:
            file_path: Path to the NetCDF file
            
        Returns:
            Dictionary with dataset information
        """
        if not HAS_NETCDF:
            logger.error("xarray not available")
            return None
        
        try:
            with xr.open_dataset(file_path) as ds:
                info = {
                    "dimensions": dict(ds.dims),
                    "variables": list(ds.variables.keys()),
                    "coordinates": list(ds.coords.keys()),
                    "attributes": dict(ds.attrs)
                }
                return info
        except Exception as e:
            logger.error(f"Error getting dataset info from {file_path}: {e}")
            return None
    
    def extract_time_series(
        self,
        file_path: str,
        variable_name: str,
        latitude: float,
        longitude: float
    ) -> Optional[List[Tuple[str, float]]]:
        """
        Extract time series data at a point.
        
        Args:
            file_path: Path to the NetCDF file
            variable_name: Name of the variable to extract
            latitude: Target latitude
            longitude: Target longitude
            
        Returns:
            List of (timestamp, value) tuples or None
        """
        if not HAS_NETCDF:
            logger.error("xarray not available")
            return None
        
        try:
            with xr.open_dataset(file_path) as ds:
                # Check if variable exists
                if variable_name not in ds.variables:
                    logger.error(f"Variable {variable_name} not found in dataset")
                    return None
                
                # Get the variable
                var = ds[variable_name]
                
                # Find dimension names
                lat_names = ['lat', 'latitude', 'Latitude', 'y']
                lon_names = ['lon', 'longitude', 'Longitude', 'x']
                time_names = ['time', 'Time', 't']
                
                lat_dim = None
                lon_dim = None
                time_dim = None
                
                for name in lat_names:
                    if name in ds.dims or name in ds.coords:
                        lat_dim = name
                        break
                
                for name in lon_names:
                    if name in ds.dims or name in ds.coords:
                        lon_dim = name
                        break
                
                for name in time_names:
                    if name in ds.dims or name in ds.coords:
                        time_dim = name
                        break
                
                if not lat_dim or not lon_dim:
                    logger.error("Could not find latitude/longitude dimensions")
                    return None
                
                if not time_dim:
                    logger.warning("No time dimension found")
                    return None
                
                # Select the point
                point = var.sel(
                    {lat_dim: latitude, lon_dim: longitude},
                    method="nearest"
                )
                
                # Extract time series
                time_series = []
                for time_val in ds[time_dim].values:
                    time_point = point.sel({time_dim: time_val})
                    value = float(time_point.values)
                    
                    if not np.isnan(value) and not np.isinf(value):
                        timestamp = str(time_val)
                        time_series.append((timestamp, value))
                
                return time_series if time_series else None
                
        except Exception as e:
            logger.error(f"Error extracting time series from {file_path}: {e}")
            return None


class HDF5Processor:
    """Processor for HDF5 files (MERRA-2)."""
    
    def __init__(self):
        """Initialize the HDF5 processor."""
        if not HAS_H5PY:
            logger.warning("h5py not installed. HDF5 processing unavailable.")
    
    def extract_variable(
        self,
        file_path: str,
        variable_path: str,
        latitude: float,
        longitude: float,
        lat_array_path: str = "lat",
        lon_array_path: str = "lon"
    ) -> Optional[float]:
        """
        Extract value at a specific point from an HDF5 file.
        
        Args:
            file_path: Path to the HDF5 file
            variable_path: Path to the variable in HDF5 structure
            latitude: Target latitude
            longitude: Target longitude
            lat_array_path: Path to latitude array
            lon_array_path: Path to longitude array
            
        Returns:
            Extracted value or None if error
        """
        if not HAS_H5PY:
            logger.error("h5py not available")
            return None
        
        try:
            with h5py.File(file_path, 'r') as f:
                # Get latitude and longitude arrays
                if lat_array_path not in f or lon_array_path not in f:
                    logger.error("Latitude or longitude arrays not found")
                    return None
                
                lats = f[lat_array_path][:]
                lons = f[lon_array_path][:]
                
                # Find nearest indices
                lat_idx = np.argmin(np.abs(lats - latitude))
                lon_idx = np.argmin(np.abs(lons - longitude))
                
                # Get the variable
                if variable_path not in f:
                    logger.error(f"Variable {variable_path} not found")
                    return None
                
                var = f[variable_path]
                
                # Extract value (handle different dimensions)
                if len(var.shape) == 2:
                    value = float(var[lat_idx, lon_idx])
                elif len(var.shape) == 3:
                    # Assume time is first dimension, take most recent
                    value = float(var[-1, lat_idx, lon_idx])
                else:
                    logger.error(f"Unsupported variable shape: {var.shape}")
                    return None
                
                # Check for fill values
                if np.isnan(value) or np.isinf(value):
                    return None
                
                return value
                
        except Exception as e:
            logger.error(f"Error extracting from HDF5 {file_path}: {e}")
            return None
    
    def list_variables(self, file_path: str) -> Optional[List[str]]:
        """
        List all variables in an HDF5 file.
        
        Args:
            file_path: Path to the HDF5 file
            
        Returns:
            List of variable paths or None
        """
        if not HAS_H5PY:
            logger.error("h5py not available")
            return None
        
        try:
            variables = []
            
            def visitor(name, obj):
                if isinstance(obj, h5py.Dataset):
                    variables.append(name)
            
            with h5py.File(file_path, 'r') as f:
                f.visititems(visitor)
            
            return variables
            
        except Exception as e:
            logger.error(f"Error listing variables in {file_path}: {e}")
            return None
