"""
User-related API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.event import UserProfile
from app.schemas.event import (
    UserProfile as UserProfileSchema,
    UserProfileCreate,
    UserProfileUpdate
)

router = APIRouter()


@router.post("/profiles", response_model=UserProfileSchema)
async def create_user_profile(
    profile_data: UserProfileCreate,
    db: Session = Depends(get_db)
):
    """Create a new user profile"""
    
    # Check if email already exists
    existing_profile = db.query(UserProfile).filter(
        UserProfile.email == profile_data.email
    ).first()
    
    if existing_profile:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new profile
    profile = UserProfile(**profile_data.dict())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return profile


@router.get("/profiles/{profile_id}", response_model=UserProfileSchema)
async def get_user_profile(profile_id: int, db: Session = Depends(get_db)):
    """Get user profile by ID"""
    
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.get("/profiles/email/{email}", response_model=UserProfileSchema)
async def get_user_profile_by_email(email: str, db: Session = Depends(get_db)):
    """Get user profile by email"""
    
    profile = db.query(UserProfile).filter(UserProfile.email == email).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.put("/profiles/{profile_id}", response_model=UserProfileSchema)
async def update_user_profile(
    profile_id: int,
    profile_update: UserProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update user profile"""
    
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update fields
    for field, value in profile_update.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return profile


@router.delete("/profiles/{profile_id}")
async def delete_user_profile(profile_id: int, db: Session = Depends(get_db)):
    """Delete user profile"""
    
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db.delete(profile)
    db.commit()
    
    return {"message": "Profile deleted successfully"}


@router.get("/profiles", response_model=List[UserProfileSchema])
async def list_user_profiles(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List user profiles (admin only)"""
    
    profiles = db.query(UserProfile).offset(skip).limit(limit).all()
    return profiles


@router.post("/profiles/{profile_id}/newsletter/subscribe")
async def subscribe_to_newsletter(profile_id: int, db: Session = Depends(get_db)):
    """Subscribe user to weekly newsletter"""
    
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile.weekly_digest = True
    db.commit()
    
    return {"message": "Successfully subscribed to newsletter"}


@router.post("/profiles/{profile_id}/newsletter/unsubscribe")
async def unsubscribe_from_newsletter(profile_id: int, db: Session = Depends(get_db)):
    """Unsubscribe user from weekly newsletter"""
    
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile.weekly_digest = False
    db.commit()
    
    return {"message": "Successfully unsubscribed from newsletter"}
