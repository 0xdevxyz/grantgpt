from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

router = APIRouter()


# Schemas
class User(BaseModel):
    id: str
    email: EmailStr
    company_name: str
    full_name: Optional[str] = None
    created_at: datetime
    subscription_tier: str


class UserUpdate(BaseModel):
    company_name: Optional[str] = None
    full_name: Optional[str] = None


class UserStats(BaseModel):
    total_applications: int
    approved_applications: int
    total_funding_received: float
    success_rate: float


@router.get("/me", response_model=User)
async def get_current_user():
    """Get current user profile"""
    # TODO: Get from auth token
    # TODO: Fetch from database
    
    mock_user = {
        "id": "user-001",
        "email": "user@example.com",
        "company_name": "Example GmbH",
        "full_name": "Max Mustermann",
        "created_at": datetime.now(),
        "subscription_tier": "basic"
    }
    
    return mock_user


@router.put("/me", response_model=User)
async def update_current_user(updates: UserUpdate):
    """Update current user profile"""
    # TODO: Update in database
    
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/me/stats", response_model=UserStats)
async def get_user_stats():
    """Get user statistics"""
    # TODO: Calculate from database
    
    return {
        "total_applications": 5,
        "approved_applications": 3,
        "total_funding_received": 750000.0,
        "success_rate": 0.60
    }

