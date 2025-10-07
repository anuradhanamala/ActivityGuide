"""
Provider submission API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.event import ProviderSubmission
from app.schemas.event import (
    ProviderSubmission as ProviderSubmissionSchema,
    ProviderSubmissionCreate
)

router = APIRouter()


@router.post("/submissions", response_model=ProviderSubmissionSchema)
async def submit_event(
    submission_data: ProviderSubmissionCreate,
    db: Session = Depends(get_db)
):
    """Submit a new event for community consideration"""
    
    # Create new submission
    submission = ProviderSubmission(**submission_data.dict())
    submission.status = "pending"
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    return submission


@router.get("/submissions/{submission_id}", response_model=ProviderSubmissionSchema)
async def get_submission(submission_id: int, db: Session = Depends(get_db)):
    """Get a specific submission by ID"""
    
    submission = db.query(ProviderSubmission).filter(
        ProviderSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return submission


@router.get("/submissions", response_model=List[ProviderSubmissionSchema])
async def list_submissions(
    status: str = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List provider submissions with optional status filter"""
    
    query = db.query(ProviderSubmission)
    
    if status:
        query = query.filter(ProviderSubmission.status == status)
    
    submissions = query.offset(skip).limit(limit).order_by(
        ProviderSubmission.created_at.desc()
    ).all()
    
    return submissions


@router.put("/submissions/{submission_id}/approve")
async def approve_submission(
    submission_id: int,
    reviewer_name: str,
    notes: str = None,
    db: Session = Depends(get_db)
):
    """Approve a provider submission (admin only)"""
    
    submission = db.query(ProviderSubmission).filter(
        ProviderSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Update submission status
    submission.status = "approved"
    submission.reviewed_by = reviewer_name
    submission.reviewed_at = datetime.now()
    submission.notes = notes
    
    # Create event from approved submission
    from app.models.event import Event
    from datetime import datetime
    
    event = Event(
        title=submission.title,
        description=submission.description,
        start_time=submission.start_time,
        end_time=submission.end_time,
        location_name=submission.location_name,
        address=submission.address,
        city=submission.city,
        state=submission.state,
        zip_code=submission.zip_code,
        category=submission.category,
        age_range_min=submission.age_range_min,
        age_range_max=submission.age_range_max,
        is_indoor=submission.is_indoor,
        is_free=submission.is_free,
        price_min=submission.price if submission.price else None,
        price_max=submission.price if submission.price else None,
        source="community_submission",
        source_id=f"submission_{submission_id}",
        source_url=None,
        tags=[submission.category] if submission.category else []
    )
    
    db.add(event)
    db.commit()
    db.refresh(submission)
    
    return submission


@router.put("/submissions/{submission_id}/reject")
async def reject_submission(
    submission_id: int,
    reviewer_name: str,
    notes: str,
    db: Session = Depends(get_db)
):
    """Reject a provider submission (admin only)"""
    
    submission = db.query(ProviderSubmission).filter(
        ProviderSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Update submission status
    submission.status = "rejected"
    submission.reviewed_by = reviewer_name
    submission.reviewed_at = datetime.now()
    submission.notes = notes
    
    db.commit()
    db.refresh(submission)
    
    return submission


@router.get("/submissions/stats/summary")
async def get_submission_stats(db: Session = Depends(get_db)):
    """Get submission statistics (admin only)"""
    
    total_submissions = db.query(ProviderSubmission).count()
    pending_submissions = db.query(ProviderSubmission).filter(
        ProviderSubmission.status == "pending"
    ).count()
    approved_submissions = db.query(ProviderSubmission).filter(
        ProviderSubmission.status == "approved"
    ).count()
    rejected_submissions = db.query(ProviderSubmission).filter(
        ProviderSubmission.status == "rejected"
    ).count()
    
    return {
        "total": total_submissions,
        "pending": pending_submissions,
        "approved": approved_submissions,
        "rejected": rejected_submissions
    }
