from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from uuid import UUID

from app.core.database import get_db
from app.models.application import Application as ApplicationModel, ApplicationStatus
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.tasks.application_tasks import generate_application_content

router = APIRouter()


# Schemas
class ProjectInfo(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    goals: List[str] = Field(default_factory=list)
    timeline_months: int = Field(..., ge=1, le=60)
    budget: float = Field(..., gt=0)
    team_size: int = Field(default=1, ge=1)
    innovation_level: str = Field(default="medium")


class ApplicationCreate(BaseModel):
    grant_id: str
    project_title: str = Field(..., min_length=3)
    project_description: str = Field(..., min_length=10)
    project_goals: Optional[List[str]] = None
    project_innovation: Optional[str] = None
    timeline_months: int = Field(..., ge=1)
    total_budget: float = Field(..., gt=0)
    requested_funding: float = Field(..., gt=0)
    own_contribution: float = Field(..., ge=0)
    team_info: Optional[Dict[str, Any]] = None
    target_audience: Optional[str] = None
    market_analysis: Optional[str] = None


class ApplicationUpdate(BaseModel):
    project_title: Optional[str] = None
    project_description: Optional[str] = None
    project_goals: Optional[List[str]] = None
    status: Optional[ApplicationStatus] = None
    total_budget: Optional[float] = None
    requested_funding: Optional[float] = None


class ApplicationResponse(BaseModel):
    id: UUID
    grant_external_id: str
    project_title: str
    project_description: str
    status: ApplicationStatus
    completion_percentage: int
    total_budget: float
    requested_funding: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ApplicationDetail(ApplicationResponse):
    project_goals: Optional[List[str]]
    project_innovation: Optional[str]
    timeline_months: int
    own_contribution: float
    team_info: Optional[Dict[str, Any]]
    generated_content: Optional[Dict[str, str]]
    compliance_score: Optional[float]
    
    class Config:
        from_attributes = True


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application: ApplicationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new grant application
    
    This endpoint creates an application and initiates AI-powered content generation.
    """
    # Validate budget
    if application.requested_funding > application.total_budget:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested funding cannot exceed total budget"
        )
    
    # Create application in database
    db_application = ApplicationModel(
        user_id=current_user.id,
        grant_external_id=application.grant_id,
        project_title=application.project_title,
        project_description=application.project_description,
        project_goals=application.project_goals,
        project_innovation=application.project_innovation,
        timeline_months=application.timeline_months,
        total_budget=application.total_budget,
        requested_funding=application.requested_funding,
        own_contribution=application.own_contribution,
        team_info=application.team_info,
        target_audience=application.target_audience,
        market_analysis=application.market_analysis,
        status=ApplicationStatus.DRAFT,
        completion_percentage=10,
        commission_rate=current_user.subscription_tier.value.get("commission_rate", 0.25)
    )
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    
    # Start AI generation in background
    background_tasks.add_task(
        generate_application_content.delay,
        str(db_application.id)
    )
    
    return db_application


@router.get("/{application_id}", response_model=ApplicationDetail)
async def get_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about an application"""
    application = db.query(ApplicationModel).filter(
        and_(
            ApplicationModel.id == application_id,
            ApplicationModel.user_id == current_user.id
        )
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return application


@router.patch("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: UUID,
    updates: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing application"""
    application = db.query(ApplicationModel).filter(
        and_(
            ApplicationModel.id == application_id,
            ApplicationModel.user_id == current_user.id
        )
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Update fields
    update_data = updates.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)
    
    application.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(application)
    
    return application


@router.get("/", response_model=List[ApplicationResponse])
async def list_applications(
    status: Optional[ApplicationStatus] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all applications for the current user"""
    query = db.query(ApplicationModel).filter(
        ApplicationModel.user_id == current_user.id
    )
    
    if status:
        query = query.filter(ApplicationModel.status == status)
    
    query = query.order_by(ApplicationModel.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    applications = query.all()
    
    return applications


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an application (only if in draft status)"""
    application = db.query(ApplicationModel).filter(
        and_(
            ApplicationModel.id == application_id,
            ApplicationModel.user_id == current_user.id
        )
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if application.status not in [ApplicationStatus.DRAFT, ApplicationStatus.GENERATING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete application that has been submitted"
        )
    
    db.delete(application)
    db.commit()
    
    return None


@router.post("/{application_id}/generate")
async def regenerate_application_content(
    application_id: UUID,
    section: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate application content
    
    If section is provided, only that section is regenerated.
    Otherwise, the entire application is regenerated.
    """
    application = db.query(ApplicationModel).filter(
        and_(
            ApplicationModel.id == application_id,
            ApplicationModel.user_id == current_user.id
        )
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Trigger AI generation
    background_tasks.add_task(
        generate_application_content.delay,
        str(application_id),
        section
    )
    
    application.status = ApplicationStatus.GENERATING
    db.commit()
    
    return {
        "message": "Generation started",
        "application_id": str(application_id),
        "section": section
    }


@router.post("/{application_id}/submit")
async def submit_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit application to grant provider"""
    application = db.query(ApplicationModel).filter(
        and_(
            ApplicationModel.id == application_id,
            ApplicationModel.user_id == current_user.id
        )
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if application.status != ApplicationStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application is not ready for submission"
        )
    
    # Update status
    application.status = ApplicationStatus.SUBMITTED
    application.submitted_at = datetime.utcnow()
    application.tracking_number = f"TRACK-{datetime.utcnow().strftime('%Y%m%d')}-{str(application_id)[:8].upper()}"
    
    db.commit()
    db.refresh(application)
    
    return {
        "message": "Application submitted successfully",
        "application_id": str(application_id),
        "tracking_number": application.tracking_number,
        "submitted_at": application.submitted_at
    }


