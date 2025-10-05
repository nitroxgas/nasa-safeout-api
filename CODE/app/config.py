"""Configuration management for the application."""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # NASA Earthdata Credentials
    earthdata_username: str = ""
    earthdata_password: str = ""
    
    # NASA FIRMS API
    firms_api_key: str = ""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    log_level: str = "INFO"
    
    # Cache Configuration
    cache_dir: str = "./cache"
    cache_expiry_hours: int = 6
    
    # Data Processing
    max_radius_meters: int = 50000
    min_radius_meters: int = 100
    default_radius_meters: int = 5000
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    
    # Application Info
    app_name: str = "NASA SafeOut API"
    app_version: str = "1.0.0"
    app_description: str = "API para consulta de dados ambientais da NASA e outras fontes"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
