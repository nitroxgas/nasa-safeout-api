"""Environmental data endpoints."""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import logging
import time

from app.models.schemas import (
    LocationRequest,
    EnvironmentalDataResponse,
    APIInfo,
    LocationInfo,
    EnvironmentalData,
    ResponseMetadata
)
from app.config import get_settings
from app.services.data_processor import DataProcessor

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.post(
    "/environmental-data",
    response_model=EnvironmentalDataResponse,
    summary="Get environmental data for a location",
    description="Returns aggregated environmental data from multiple sources for a specific location"
)
async def get_environmental_data(request: LocationRequest):
    """
    Get environmental data for a specific location.
    
    - **latitude**: Latitude in decimal degrees (-90 to 90)
    - **longitude**: Longitude in decimal degrees (-180 to 180)
    - **radius_meters**: Search radius in meters (100 to 50000)
    """
    start_time = time.time()
    
    try:
        logger.info(
            f"Processing request for location: ({request.latitude}, {request.longitude}), "
            f"radius: {request.radius_meters}m"
        )
        
        # Initialize data processor
        processor = DataProcessor()
        
        # Collect data from all sources
        data_sources_queried = 0
        data_sources_successful = 0
        warnings = []
        
        # Initialize environmental data
        env_data = EnvironmentalData()
        
        # TODO: Implement actual data fetching
        # For now, return a placeholder response
        logger.warning("Data fetching not yet implemented - returning placeholder data")
        warnings.append("Data fetching not yet implemented - placeholder data returned")
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Build response
        response = EnvironmentalDataResponse(
            location=LocationInfo(
                latitude=request.latitude,
                longitude=request.longitude,
                radius_meters=request.radius_meters
            ),
            timestamp=datetime.utcnow().isoformat() + "Z",
            data=env_data,
            metadata=ResponseMetadata(
                processing_time_ms=processing_time,
                data_sources_queried=data_sources_queried,
                data_sources_successful=data_sources_successful,
                warnings=warnings
            )
        )
        
        logger.info(f"Request processed successfully in {processing_time}ms")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )


@router.get(
    "/info",
    response_model=APIInfo,
    summary="Get API information",
    description="Returns information about the API and its data sources"
)
async def get_api_info():
    """Get API information and capabilities."""
    return APIInfo(
        name=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        data_sources=[
            {
                "name": "GPM IMERG",
                "type": "precipitation",
                "provider": "NASA",
                "update_frequency": "30 minutes"
            },
            {
                "name": "TROPOMI/Sentinel-5P",
                "type": "air_quality",
                "provider": "ESA/NASA",
                "update_frequency": "daily"
            },
            {
                "name": "OpenAQ",
                "type": "air_quality_ground",
                "provider": "OpenAQ",
                "update_frequency": "hourly"
            },
            {
                "name": "MERRA-2",
                "type": "weather",
                "provider": "NASA",
                "update_frequency": "hourly"
            },
            {
                "name": "NASA FIRMS",
                "type": "fire_detection",
                "provider": "NASA",
                "update_frequency": "near real-time"
            }
        ],
        limits={
            "max_radius_meters": settings.max_radius_meters,
            "min_radius_meters": settings.min_radius_meters,
            "rate_limit": f"{settings.rate_limit_per_minute} requests per minute"
        }
    )
