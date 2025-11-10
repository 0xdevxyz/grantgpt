from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class DocumentType(str, enum.Enum):
    """Document types"""
    FULL_APPLICATION = "full_application"
    PROJECT_DESCRIPTION = "project_description"
    MARKET_ANALYSIS = "market_analysis"
    TECHNICAL_FEASIBILITY = "technical_feasibility"
    WORK_PLAN = "work_plan"
    FINANCIAL_PLAN = "financial_plan"
    RISK_MANAGEMENT = "risk_management"
    UTILIZATION_PLAN = "utilization_plan"
    APPROVAL_NOTICE = "approval_notice"  # User uploads this


class DocumentFormat(str, enum.Enum):
    """Document formats"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    JSON = "json"


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False, index=True)
    
    # Document Info
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    format = Column(SQLEnum(DocumentFormat), nullable=False)
    filename = Column(String, nullable=False)
    
    # Storage
    file_path = Column(String, nullable=False)  # Path in storage system
    file_size = Column(Integer, nullable=True)  # Size in bytes
    
    # Generation
    generated_by_ai = Column(Boolean, default=False, nullable=False)
    generation_duration_seconds = Column(Integer, nullable=True)
    
    # Version Control
    version = Column(Integer, default=1, nullable=False)
    is_latest = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    application = relationship("Application", back_populates="documents")
    
    def __repr__(self):
        return f"<Document {self.filename} ({self.document_type.value})>"

