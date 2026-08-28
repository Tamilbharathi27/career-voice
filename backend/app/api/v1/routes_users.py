from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, Profile, UserRole
from app.schemas.user import UserResponse, ProfileUpdate, ProfileResponse
from app.core.deps import get_current_user, require_recruiter

router = APIRouter(prefix="/users", tags=["Users & Profiles"])

@router.get("/profile", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve the current user's profile."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("/profile", response_model=ProfileResponse)
def update_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update profile information (target role, skills, experience level, bio)."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile

@router.get("/candidates", response_model=List[UserResponse])
def get_candidates(
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    """Recruiter endpoint: List all candidate profiles for review."""
    candidates = db.query(User).filter(User.role == UserRole.STUDENT.value).all()
    return candidates
