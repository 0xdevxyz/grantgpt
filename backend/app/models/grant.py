from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class GrantType(str, enum.Enum):
    """Grant types"""
    FEDERAL = "federal"
    STATE = "state"
    EU = "eu"
    MUNICIPAL = "municipal"


class GrantCategory(str, enum.Enum):
    """Grant categories"""
    INNOVATION = "innovation"
    DIGITALIZATION = "digitalization"
    GREEN_TECH = "green_tech"
    EXPORT = "export"
    TRAINING = "training"
    REGIONAL = "regional"


class Grant(Base):
    __tablename__ = "grants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, unique=True, nullable=False, index=True)  # e.g., "zim-2024-001"
    
    # Basic info
    name = Column(String, nullable=False)
    type = Column(SQLEnum(GrantType), nullable=False, index=True)
    category = Column(SQLEnum(GrantCategory), nullable=False, index=True)
    
    # Financial
    max_funding = Column(Float, nullable=False)  # Maximum funding amount in EUR
    min_funding = Column(Float, nullable=True)
    min_own_contribution_percent = Column(Float, nullable=True)  # e.g., 15
    
    # Details
    description = Column(Text, nullable=False)
    guidelines = Column(Text, nullable=True)  # Detailed guidelines
    
    # Eligibility
    eligibility = Column(JSON, nullable=True)  # List of requirements
    requirements = Column(JSON, nullable=True)  # Detailed requirements
    
    # Process
    application_process = Column(Text, nullable=True)
    duration_months = Column(Integer, nullable=True)
    
    # Deadlines
    deadline = Column(DateTime, nullable=True)
    is_continuous = Column(Boolean, default=False, nullable=False)
    
    # Success metrics
    historical_success_rate = Column(Float, nullable=True)  # e.g., 0.65 = 65%
    avg_funded_amount = Column(Float, nullable=True)
    
    # Contact
    contact_info = Column(JSON, nullable=True)
    website_url = Column(String, nullable=True)
    
    # Vector embedding (stored as JSON for compatibility)
    embedding_metadata = Column(JSON, nullable=True)  # Store model info
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Grant {self.name} ({self.external_id})>"

