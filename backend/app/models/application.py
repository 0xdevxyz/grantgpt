from sqlalchemy import Column, String, Float, DateTime, Text, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class ApplicationStatus(str, enum.Enum):
    """Application status workflow"""
    DRAFT = "draft"
    GENERATING = "generating"
    REVIEW = "review"
    READY = "ready"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    grant_external_id = Column(String, nullable=False, index=True)  # Reference to grant
    
    # Project Info
    project_title = Column(String, nullable=False)
    project_description = Column(Text, nullable=False)
    project_goals = Column(JSON, nullable=True)  # List of goals
    project_innovation = Column(Text, nullable=True)
    project_technology = Column(Text, nullable=True)
    timeline_months = Column(Integer, nullable=False)
    
    # Budget
    total_budget = Column(Float, nullable=False)
    requested_funding = Column(Float, nullable=False)
    own_contribution = Column(Float, nullable=False)
    budget_breakdown = Column(JSON, nullable=True)  # Detailed breakdown
    
    # Team
    team_info = Column(JSON, nullable=True)
    
    # Market
    target_audience = Column(Text, nullable=True)
    market_analysis = Column(Text, nullable=True)
    business_model = Column(Text, nullable=True)
    
    # Generated Content (AI-written sections)
    generated_content = Column(JSON, nullable=True)  # {section_name: content}
    
    # Compliance
    compliance_score = Column(Float, nullable=True)  # 0-100
    compliance_checks = Column(JSON, nullable=True)  # Detailed check results
    
    # Status
    status = Column(
        SQLEnum(ApplicationStatus),
        default=ApplicationStatus.DRAFT,
        nullable=False,
        index=True
    )
    completion_percentage = Column(Integer, default=0, nullable=False)
    
    # Submission
    submitted_at = Column(DateTime, nullable=True)
    tracking_number = Column(String, nullable=True)
    
    # Result
    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    approved_funding = Column(Float, nullable=True)  # Actual approved amount
    
    # Billing (success-based)
    commission_rate = Column(Float, nullable=True)  # 0.40, 0.50, or 0.60
    commission_amount = Column(Float, nullable=True)  # Calculated after approval
    commission_paid = Column(Boolean, default=False, nullable=False)
    commission_paid_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="applications")
    documents = relationship("Document", back_populates="application", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Application {self.project_title} ({self.status.value})>"

