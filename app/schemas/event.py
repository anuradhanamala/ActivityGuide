"""
Pydantic schemas for event-related data
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


class EventBase(BaseModel):
    """Base event schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    location_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    age_range_min: Optional[int] = Field(None, ge=0, le=18)
    age_range_max: Optional[int] = Field(None, ge=0, le=18)
    is_indoor: Optional[bool] = True
    is_free: Optional[bool] = False
    price_min: Optional[float] = Field(None, ge=0)
    price_max: Optional[float] = Field(None, ge=0)
    source: str
    source_id: str
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None


class EventCreate(EventBase):
    """Schema for creating events"""
    pass


class EventUpdate(BaseModel):
    """Schema for updating events"""
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    age_range_min: Optional[int] = Field(None, ge=0, le=18)
    age_range_max: Optional[int] = Field(None, ge=0, le=18)
    is_indoor: Optional[bool] = None
    is_free: Optional[bool] = None
    price_min: Optional[float] = Field(None, ge=0)
    price_max: Optional[float] = Field(None, ge=0)
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None


class Event(EventBase):
    """Complete event schema"""
    id: int
    summary: Optional[str] = None
    capacity: Optional[int] = None
    is_active: bool = True
    last_synced: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EventSearchFilters(BaseModel):
    """Schema for event search filters"""
    zip_code: str = Field(..., min_length=5, max_length=10)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[str] = None
    age_min: Optional[int] = Field(None, ge=0, le=18)
    age_max: Optional[int] = Field(None, ge=0, le=18)
    is_indoor: Optional[bool] = None
    is_free: Optional[bool] = None
    price_max: Optional[float] = Field(None, ge=0)
    max_distance_miles: Optional[int] = Field(25, ge=1, le=100)
    limit: Optional[int] = Field(20, ge=1, le=100)


class EventSearchResponse(BaseModel):
    """Schema for event search response"""
    events: List[Event]
    total_count: int
    filters_applied: Dict[str, Any]
    search_summary: Optional[str] = None  # AI-generated summary


class UserProfileBase(BaseModel):
    """Base user profile schema"""
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    name: Optional[str] = None
    default_zip_code: Optional[str] = None
    max_distance_miles: Optional[int] = Field(25, ge=1, le=100)
    children_ages: Optional[List[int]] = Field(None, description="List of child ages")
    preferred_categories: Optional[List[str]] = None
    preferred_activity_types: Optional[List[str]] = None
    email_notifications: Optional[bool] = True
    weekly_digest: Optional[bool] = True


class UserProfileCreate(UserProfileBase):
    """Schema for creating user profiles"""
    pass


class UserProfileUpdate(BaseModel):
    """Schema for updating user profiles"""
    name: Optional[str] = None
    default_zip_code: Optional[str] = None
    max_distance_miles: Optional[int] = Field(None, ge=1, le=100)
    children_ages: Optional[List[int]] = None
    preferred_categories: Optional[List[str]] = None
    preferred_activity_types: Optional[List[str]] = None
    email_notifications: Optional[bool] = None
    weekly_digest: Optional[bool] = None


class UserProfile(UserProfileBase):
    """Complete user profile schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProviderSubmissionBase(BaseModel):
    """Base provider submission schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    location_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    category: Optional[str] = None
    age_range_min: Optional[int] = Field(None, ge=0, le=18)
    age_range_max: Optional[int] = Field(None, ge=0, le=18)
    is_indoor: Optional[bool] = True
    is_free: Optional[bool] = False
    price: Optional[float] = Field(None, ge=0)


class ProviderSubmissionCreate(ProviderSubmissionBase):
    """Schema for creating provider submissions"""
    pass


class ProviderSubmission(ProviderSubmissionBase):
    """Complete provider submission schema"""
    id: int
    status: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
