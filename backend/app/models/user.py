from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class SubscriptionTier(str, enum.Enum):
    """Subscription tiers for revenue model"""
    TIER_1 = "tier_1"  # 40% commission
    TIER_2 = "tier_2"  # 50% commission
    TIER_3 = "tier_3"  # 60% commission


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    
    # Profile
    full_name = Column(String, nullable=True)
    company_name = Column(String, nullable=False)
    company_size = Column(Integer, nullable=True)  # Number of employees
    industry = Column(String, nullable=True)
    annual_revenue = Column(Integer, nullable=True)  # in EUR
    location = Column(String, nullable=True)  # City, State
    technology_stack = Column(String, nullable=True)  # Comma-separated
    
    # Subscription
    subscription_tier = Column(
        SQLEnum(SubscriptionTier),
        default=SubscriptionTier.TIER_1,
        nullable=False
    )
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"

