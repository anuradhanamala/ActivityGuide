"""
Enhanced unified event models for multi-source data integration
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum
from typing import Dict, Any, Optional
import uuid


class EventSource(str, enum.Enum):
    """Enum for event data sources"""
    EVENTBRITE = "eventbrite"
    YELP = "yelp"
    GOOGLE_PLACES = "google_places"
    TICKETMASTER = "ticketmaster"
    MEETUP = "meetup"
    RECREATION_GOV = "recreation_gov"
    YMCA = "ymca"
    BOYS_GIRLS_CLUB = "boys_girls_club"
    OPENSTREETMAP = "openstreetmap"
    COMMUNITY = "community"  # For provider submissions


class EventType(str, enum.Enum):
    """Enum for event types"""
    EVENT = "event"  # Time-bound activities
    VENUE = "venue"  # Permanent locations
    CLASS = "class"  # Recurring classes
    PROGRAM = "program"  # Ongoing programs


class AgeCategory(str, enum.Enum):
    """Enum for age categories"""
    TODDLER = "toddler"  # 0-2
    PRESCHOOL = "preschool"  # 3-5
    ELEMENTARY = "elementary"  # 6-11
    MIDDLE_SCHOOL = "middle_school"  # 12-14
    HIGH_SCHOOL = "high_school"  # 15-17
    ALL_AGES = "all_ages"
    FAMILY = "family"


class UnifiedEvent(Base):
    """
    Unified event model that can store data from all sources
    with enhanced fields for comprehensive event management
    """
    
    __tablename__ = "unified_events"
    
    # Primary key and identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    external_id = Column(String(100), nullable=False, index=True)  # Source-specific ID
    source = Column(Enum(EventSource), nullable=False, index=True)
    event_type = Column(Enum(EventType), default=EventType.EVENT, index=True)
    
    # Basic event information
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    summary = Column(Text)  # AI-generated summary
    short_description = Column(String(500))  # Brief description for cards
    
    # Timing information
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime)
    start_date = Column(DateTime, index=True)  # For events without specific time
    end_date = Column(DateTime)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(JSON)  # RRULE format for recurring events
    
    # Location information
    location_name = Column(String(255), index=True)
    venue_name = Column(String(255))  # Specific venue within location
    address = Column(String(500))
    street_address = Column(String(255))
    city = Column(String(100), index=True)
    state = Column(String(50), index=True)
    zip_code = Column(String(10), index=True)
    country = Column(String(50), default="US")
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    location_accuracy = Column(String(50))  # exact, approximate, city_level
    
    # Categorization
    primary_category = Column(String(100), index=True)
    secondary_categories = Column(JSON)  # Array of secondary categories
    subcategory = Column(String(100))
    tags = Column(JSON)  # Array of tags for flexible filtering
    
    # Age and audience targeting
    age_range_min = Column(Integer)
    age_range_max = Column(Integer)
    age_categories = Column(JSON)  # Array of AgeCategory enums
    target_audience = Column(JSON)  # Array: children, teens, families, adults
    
    # Physical characteristics
    is_indoor = Column(Boolean, index=True)
    is_outdoor = Column(Boolean, index=True)
    is_virtual = Column(Boolean, default=False)
    is_accessible = Column(Boolean)  # ADA accessible
    weather_dependent = Column(Boolean, default=False)
    
    # Pricing information
    is_free = Column(Boolean, index=True)
    price_min = Column(Float)
    price_max = Column(Float)
    price_currency = Column(String(3), default="USD")
    pricing_model = Column(String(50))  # per_person, per_family, per_class, per_month
    pricing_notes = Column(Text)
    
    # Capacity and availability
    capacity = Column(Integer)
    current_registrations = Column(Integer)
    is_full = Column(Boolean, default=False)
    requires_registration = Column(Boolean, default=False)
    registration_deadline = Column(DateTime)
    
    # Contact and booking information
    contact_name = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    booking_url = Column(String(500))
    registration_url = Column(String(500))
    
    # Media and resources
    image_url = Column(String(500))
    image_urls = Column(JSON)  # Array of additional image URLs
    video_url = Column(String(500))
    website_url = Column(String(500))
    social_media_urls = Column(JSON)  # Array of social media links
    
    # Source-specific data
    source_url = Column(String(500))
    source_data = Column(JSON)  # Raw data from source API
    source_rating = Column(Float)  # Rating from source (if available)
    source_review_count = Column(Integer)
    
    # Quality and validation
    data_quality_score = Column(Float, default=1.0)  # 0-1 score for data completeness
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime)
    verified_by = Column(String(255))
    
    # Activity level and requirements
    activity_level = Column(String(50))  # low, moderate, high
    skill_level = Column(String(50))  # beginner, intermediate, advanced
    equipment_required = Column(JSON)  # Array of required equipment
    prerequisites = Column(Text)
    
    # Seasonal and scheduling
    is_seasonal = Column(Boolean, default=False)
    season_start = Column(String(20))  # spring, summer, fall, winter
    season_end = Column(String(20))
    is_holiday_specific = Column(Boolean, default=False)
    holiday_type = Column(String(50))
    
    # Metadata and tracking
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False)
    priority_score = Column(Float, default=0.0)  # For ranking in search results
    view_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_synced = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)  # When to stop showing this event
    
    # Relationships and references
    related_events = Column(JSON)  # Array of related event IDs
    parent_event_id = Column(UUID(as_uuid=True))  # For recurring events
    organization_id = Column(String(100))  # Link to organization/provider
    
    def __repr__(self):
        return f"<UnifiedEvent(id={self.id}, title='{self.title}', source='{self.source}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': str(self.id),
            'external_id': self.external_id,
            'source': self.source.value,
            'event_type': self.event_type.value,
            'title': self.title,
            'description': self.description,
            'summary': self.summary,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'location_name': self.location_name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'primary_category': self.primary_category,
            'tags': self.tags,
            'age_range_min': self.age_range_min,
            'age_range_max': self.age_range_max,
            'is_indoor': self.is_indoor,
            'is_free': self.is_free,
            'price_min': self.price_min,
            'price_max': self.price_max,
            'image_url': self.image_url,
            'source_url': self.source_url,
            'booking_url': self.booking_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EventProvider(Base):
    """
    Model for tracking event providers and organizations
    """
    
    __tablename__ = "event_providers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    organization_type = Column(String(100))  # ymca, boys_girls_club, city_park, etc.
    description = Column(Text)
    
    # Contact information
    email = Column(String(255))
    phone = Column(String(50))
    website = Column(String(500))
    
    # Location
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Metadata
    is_verified = Column(Boolean, default=False)
    data_source = Column(String(100))
    external_id = Column(String(100))
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<EventProvider(id={self.id}, name='{self.name}')>"


class EventCategory(Base):
    """
    Standardized categories for events across all sources
    """
    
    __tablename__ = "event_categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_category_id = Column(Integer)  # For hierarchical categories
    icon = Column(String(100))  # Icon name or URL
    color = Column(String(7))  # Hex color code
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<EventCategory(id={self.id}, name='{self.name}')>"


class EventSyncLog(Base):
    """
    Log for tracking sync operations from different sources
    """
    
    __tablename__ = "event_sync_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(Enum(EventSource), nullable=False)
    sync_type = Column(String(50))  # full, incremental, manual
    status = Column(String(50))  # success, partial, failed
    events_processed = Column(Integer, default=0)
    events_created = Column(Integer, default=0)
    events_updated = Column(Integer, default=0)
    events_deleted = Column(Integer, default=0)
    errors = Column(JSON)  # Array of error messages
    sync_duration_seconds = Column(Float)
    
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<EventSyncLog(id={self.id}, source='{self.source}', status='{self.status}')>"
