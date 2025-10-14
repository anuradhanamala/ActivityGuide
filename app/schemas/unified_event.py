"""
Pydantic schemas for unified events
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

from app.models.unified_event import EventSource, EventType, AgeCategory


class UnifiedEventBase(BaseModel):
    """Base schema for unified events"""
    
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    summary: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[Dict[str, Any]] = None
    
    # Location
    location_name: Optional[str] = None
    venue_name: Optional[str] = None
    address: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "US"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Categorization
    primary_category: Optional[str] = None
    secondary_categories: Optional[List[str]] = None
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None
    
    # Age targeting
    age_range_min: Optional[int] = Field(None, ge=0, le=18)
    age_range_max: Optional[int] = Field(None, ge=0, le=18)
    age_categories: Optional[List[AgeCategory]] = None
    target_audience: Optional[List[str]] = None
    
    # Physical characteristics
    is_indoor: Optional[bool] = None
    is_outdoor: Optional[bool] = None
    is_virtual: bool = False
    is_accessible: Optional[bool] = None
    weather_dependent: bool = False
    
    # Pricing
    is_free: Optional[bool] = None
    price_min: Optional[float] = Field(None, ge=0)
    price_max: Optional[float] = Field(None, ge=0)
    price_currency: str = "USD"
    pricing_model: Optional[str] = None
    pricing_notes: Optional[str] = None
    
    # Capacity
    capacity: Optional[int] = Field(None, ge=1)
    current_registrations: Optional[int] = Field(None, ge=0)
    is_full: bool = False
    requires_registration: bool = False
    registration_deadline: Optional[datetime] = None
    
    # Contact
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    booking_url: Optional[str] = None
    registration_url: Optional[str] = None
    
    # Media
    image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    video_url: Optional[str] = None
    website_url: Optional[str] = None
    social_media_urls: Optional[List[str]] = None
    
    # Source data
    source_url: Optional[str] = None
    source_data: Optional[Dict[str, Any]] = None
    source_rating: Optional[float] = Field(None, ge=0, le=5)
    source_review_count: Optional[int] = Field(None, ge=0)
    
    # Quality
    data_quality_score: float = Field(1.0, ge=0, le=1)
    is_verified: bool = False
    verification_date: Optional[datetime] = None
    verified_by: Optional[str] = None
    
    # Activity details
    activity_level: Optional[str] = None
    skill_level: Optional[str] = None
    equipment_required: Optional[List[str]] = None
    prerequisites: Optional[str] = None
    
    # Seasonal
    is_seasonal: bool = False
    season_start: Optional[str] = None
    season_end: Optional[str] = None
    is_holiday_specific: bool = False
    holiday_type: Optional[str] = None
    
    # Metadata
    is_featured: bool = False
    priority_score: float = 0.0
    view_count: int = 0
    click_count: int = 0
    
    @validator('age_range_max')
    def age_max_greater_than_min(cls, v, values):
        if v is not None and values.get('age_range_min') is not None:
            if v < values['age_range_min']:
                raise ValueError('age_range_max must be greater than or equal to age_range_min')
        return v
    
    @validator('price_max')
    def price_max_greater_than_min(cls, v, values):
        if v is not None and values.get('price_min') is not None:
            if v < values['price_min']:
                raise ValueError('price_max must be greater than or equal to price_min')
        return v
    
    @validator('end_time')
    def end_time_after_start(cls, v, values):
        if v is not None and values.get('start_time') is not None:
            if v <= values['start_time']:
                raise ValueError('end_time must be after start_time')
        return v


class UnifiedEventCreate(UnifiedEventBase):
    """Schema for creating unified events"""
    
    external_id: str = Field(..., min_length=1, max_length=100)
    source: EventSource
    event_type: EventType = EventType.EVENT


class UnifiedEventUpdate(BaseModel):
    """Schema for updating unified events"""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    summary: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    
    # Allow updating most fields
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    primary_category: Optional[str] = None
    secondary_categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    
    age_range_min: Optional[int] = Field(None, ge=0, le=18)
    age_range_max: Optional[int] = Field(None, ge=0, le=18)
    
    is_indoor: Optional[bool] = None
    is_outdoor: Optional[bool] = None
    is_free: Optional[bool] = None
    price_min: Optional[float] = Field(None, ge=0)
    price_max: Optional[float] = Field(None, ge=0)
    
    capacity: Optional[int] = Field(None, ge=1)
    is_full: Optional[bool] = None
    requires_registration: Optional[bool] = None
    
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    booking_url: Optional[str] = None
    
    image_url: Optional[str] = None
    website_url: Optional[str] = None
    
    data_quality_score: Optional[float] = Field(None, ge=0, le=1)
    is_verified: Optional[bool] = None
    is_featured: Optional[bool] = None
    priority_score: Optional[float] = None


class UnifiedEventResponse(UnifiedEventBase):
    """Schema for unified event responses"""
    
    id: str
    external_id: str
    source: EventSource
    event_type: EventType
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_synced: datetime
    expires_at: Optional[datetime] = None
    
    # Relationships
    related_events: Optional[List[str]] = None
    parent_event_id: Optional[str] = None
    organization_id: Optional[str] = None
    
    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to handle UUID conversion"""
        data = {
            'id': str(obj.id) if obj.id else None,
            'external_id': obj.external_id,
            'source': obj.source,
            'event_type': obj.event_type,
            'title': obj.title,
            'description': obj.description,
            'summary': obj.summary,
            'short_description': obj.short_description,
            'start_time': obj.start_time,
            'end_time': obj.end_time,
            'start_date': obj.start_date,
            'end_date': obj.end_date,
            'is_recurring': obj.is_recurring,
            'recurrence_pattern': obj.recurrence_pattern,
            'location_name': obj.location_name,
            'venue_name': obj.venue_name,
            'address': obj.address,
            'street_address': obj.street_address,
            'city': obj.city,
            'state': obj.state,
            'zip_code': obj.zip_code,
            'country': obj.country,
            'latitude': obj.latitude,
            'longitude': obj.longitude,
            'primary_category': obj.primary_category,
            'secondary_categories': obj.secondary_categories,
            'subcategory': obj.subcategory,
            'tags': obj.tags,
            'age_range_min': obj.age_range_min,
            'age_range_max': obj.age_range_max,
            'age_categories': obj.age_categories,
            'target_audience': obj.target_audience,
            'is_indoor': obj.is_indoor,
            'is_outdoor': obj.is_outdoor,
            'is_virtual': obj.is_virtual,
            'is_accessible': obj.is_accessible,
            'weather_dependent': obj.weather_dependent,
            'is_free': obj.is_free,
            'price_min': obj.price_min,
            'price_max': obj.price_max,
            'price_currency': obj.price_currency,
            'pricing_model': obj.pricing_model,
            'pricing_notes': obj.pricing_notes,
            'capacity': obj.capacity,
            'current_registrations': obj.current_registrations,
            'is_full': obj.is_full,
            'requires_registration': obj.requires_registration,
            'registration_deadline': obj.registration_deadline,
            'contact_name': obj.contact_name,
            'contact_email': obj.contact_email,
            'contact_phone': obj.contact_phone,
            'booking_url': obj.booking_url,
            'registration_url': obj.registration_url,
            'image_url': obj.image_url,
            'image_urls': obj.image_urls,
            'video_url': obj.video_url,
            'website_url': obj.website_url,
            'social_media_urls': obj.social_media_urls,
            'source_url': obj.source_url,
            'source_data': obj.source_data,
            'source_rating': obj.source_rating,
            'source_review_count': obj.source_review_count,
            'data_quality_score': obj.data_quality_score,
            'is_verified': obj.is_verified,
            'verification_date': obj.verification_date,
            'verified_by': obj.verified_by,
            'activity_level': obj.activity_level,
            'skill_level': obj.skill_level,
            'equipment_required': obj.equipment_required,
            'prerequisites': obj.prerequisites,
            'is_seasonal': obj.is_seasonal,
            'season_start': obj.season_start,
            'season_end': obj.season_end,
            'is_holiday_specific': obj.is_holiday_specific,
            'holiday_type': obj.holiday_type,
            'is_featured': obj.is_featured,
            'priority_score': obj.priority_score,
            'view_count': obj.view_count,
            'click_count': obj.click_count,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
            'last_synced': obj.last_synced,
            'expires_at': obj.expires_at,
            'related_events': obj.related_events,
            'parent_event_id': str(obj.parent_event_id) if obj.parent_event_id else None,
            'organization_id': obj.organization_id,
        }
        return cls(**data)
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            EventSource: lambda v: v.value,
            EventType: lambda v: v.value,
            AgeCategory: lambda v: v.value if isinstance(v, AgeCategory) else v
        }


class EventSearchRequest(BaseModel):
    """Schema for event search requests"""
    
    zip_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    radius_miles: int = Field(25, ge=1, le=100)
    
    categories: Optional[List[str]] = None
    age_min: Optional[int] = Field(None, ge=0, le=18)
    age_max: Optional[int] = Field(None, ge=0, le=18)
    
    is_free: Optional[bool] = None
    is_indoor: Optional[bool] = None
    event_type: Optional[EventType] = None
    sources: Optional[List[EventSource]] = None
    
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class EventSearchResponse(BaseModel):
    """Schema for event search responses"""
    
    events: List[UnifiedEventResponse]
    total_count: int
    search_summary: str
    filters_applied: Dict[str, Any]
    
    # Pagination
    page: int = 1
    per_page: int = 20
    total_pages: int = 1
    
    # Source breakdown
    source_counts: Optional[Dict[str, int]] = None
    category_counts: Optional[Dict[str, int]] = None


class EventSourceInfo(BaseModel):
    """Schema for event source information"""
    
    name: str
    display_name: str
    description: str
    is_available: bool = True
    api_configured: bool = False
    last_sync: Optional[datetime] = None
    event_count: int = 0


class SyncStatus(BaseModel):
    """Schema for sync status"""
    
    source: Optional[str] = None
    sync_type: str
    status: str
    events_processed: int = 0
    events_created: int = 0
    events_updated: int = 0
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    errors: Optional[List[str]] = None


class EventStats(BaseModel):
    """Schema for event statistics"""
    
    total_events: int
    active_events: int
    events_by_source: Dict[str, int]
    events_by_category: Dict[str, int]
    events_by_type: Dict[str, int]
    free_events: int
    indoor_events: int
    outdoor_events: int
    last_updated: datetime


class BulkEventUpdate(BaseModel):
    """Schema for bulk event updates"""
    
    event_ids: List[str]
    updates: UnifiedEventUpdate
    reason: Optional[str] = None


class EventValidationResult(BaseModel):
    """Schema for event validation results"""
    
    event_id: str
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    quality_score: float
    suggestions: List[str] = []
