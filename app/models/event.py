"""
Event database models
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Event(Base):
    """Event model for storing activity events"""
    
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    summary = Column(Text)  # AI-generated summary
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime)
    location_name = Column(String(255))
    address = Column(String(500))
    city = Column(String(100), index=True)
    state = Column(String(50), index=True)
    zip_code = Column(String(10), index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Event details
    category = Column(String(100), index=True)
    subcategory = Column(String(100))
    age_range_min = Column(Integer)
    age_range_max = Column(Integer)
    is_indoor = Column(Boolean, default=True)
    is_free = Column(Boolean, default=False)
    price_min = Column(Float)
    price_max = Column(Float)
    capacity = Column(Integer)
    
    # External data
    source = Column(String(50), nullable=False)  # eventbrite, yelp, google, etc.
    source_id = Column(String(100), nullable=False)
    source_url = Column(String(500))
    image_url = Column(String(500))
    tags = Column(JSON)  # Array of tags
    
    # Metadata
    is_active = Column(Boolean, default=True, index=True)
    last_synced = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Event(id={self.id}, title='{self.title}', start_time='{self.start_time}')>"


class UserProfile(Base):
    """User profile model for personalization"""
    
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    
    # Location preferences
    default_zip_code = Column(String(10))
    max_distance_miles = Column(Integer, default=25)
    
    # Child information
    children_ages = Column(JSON)  # Array of child ages
    preferred_categories = Column(JSON)  # Array of preferred categories
    preferred_activity_types = Column(JSON)  # indoor/outdoor preferences
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    weekly_digest = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, email='{self.email}')>"


class ProviderSubmission(Base):
    """Community event submissions"""
    
    __tablename__ = "provider_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    location_name = Column(String(255))
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(10))
    
    # Contact information
    contact_name = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    
    # Event details
    category = Column(String(100))
    age_range_min = Column(Integer)
    age_range_max = Column(Integer)
    is_indoor = Column(Boolean, default=True)
    is_free = Column(Boolean, default=False)
    price = Column(Float)
    
    # Status
    status = Column(String(50), default="pending")  # pending, approved, rejected
    reviewed_by = Column(String(255))
    reviewed_at = Column(DateTime)
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ProviderSubmission(id={self.id}, title='{self.title}', status='{self.status}')>"
