"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    SECRET_KEY: str = "your-secret-key-change-in-production"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "sqlite:///./activityguide.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API Keys - Existing
    EVENTBRITE_API_KEY: Optional[str] = None
    YELP_API_KEY: Optional[str] = None
    GOOGLE_PLACES_API_KEY: Optional[str] = None
    TICKETMASTER_API_KEY: Optional[str] = None
    
    # API Keys - New Sources
    MEETUP_API_KEY: Optional[str] = None
    RECREATION_GOV_API_KEY: Optional[str] = None
    YMCA_API_KEY: Optional[str] = None  # May not exist, using web scraping
    BOYS_GIRLS_CLUB_API_KEY: Optional[str] = None  # May not exist, using web scraping
    
    # OpenStreetMap doesn't require API key but we can track usage
    OSM_USER_AGENT: str = "ActivityGuide/1.0 (Family Event Discovery)"
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None  # For Gemini
    PARALLEL_AI_API_KEY: Optional[str] = None  # Deprecated - kept for backward compatibility with .env
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Sync Settings
    SYNC_INTERVAL_HOURS: int = 6  # How often to sync with external APIs
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
