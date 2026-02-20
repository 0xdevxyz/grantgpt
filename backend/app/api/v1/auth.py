"""
Authentication API Routes
Complete implementation with database integration.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from uuid import UUID
import secrets

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, SubscriptionTier

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# =============================================================================
# Schemas
# =============================================================================

class UserRegister(BaseModel):
    """User registration schema."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    company_name: str = Field(..., min_length=2)
    full_name: Optional[str] = None
    company_size: Optional[int] = None
    industry: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT Token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """Token payload data."""
    email: Optional[str] = None
    user_id: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema."""
    id: UUID
    email: str
    full_name: Optional[str]
    company_name: str
    company_size: Optional[int]
    industry: Optional[str]
    subscription_tier: SubscriptionTier
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update schema."""
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    company_size: Optional[int] = None
    industry: Optional[str] = None
    annual_revenue: Optional[int] = None
    location: Optional[str] = None
    technology_stack: Optional[str] = None


class PasswordChange(BaseModel):
    """Password change schema."""
    current_password: str
    new_password: str = Field(..., min_length=8)


class PasswordReset(BaseModel):
    """Password reset request schema."""
    email: EmailStr


# =============================================================================
# Helper Functions
# =============================================================================

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if email is None:
            raise credentials_exception
            
        token_data = TokenData(email=email, user_id=user_id)
        
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_email(db, email=token_data.email)
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


# =============================================================================
# API Routes
# =============================================================================

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Creates a new user account with the provided information.
    Returns a JWT access token upon successful registration.
    """
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        company_name=user_data.company_name,
        company_size=user_data.company_size,
        industry=user_data.industry,
        subscription_tier=SubscriptionTier.TIER_1,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # TODO: Send verification email in background
    # background_tasks.add_task(send_verification_email, new_user.email)
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": new_user.email,
            "user_id": str(new_user.id)
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRATION_HOURS * 3600
    }


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login and get access token.
    
    Authenticates user with email and password.
    Returns a JWT access token upon successful authentication.
    """
    # Get user
    user = get_user_by_email(db, form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": str(user.id)
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRATION_HOURS * 3600
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's profile.
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    """
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password.
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/forgot-password")
async def forgot_password(
    reset_data: PasswordReset,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request password reset.
    
    Sends a password reset email if the user exists.
    Always returns success to prevent email enumeration.
    """
    user = get_user_by_email(db, reset_data.email)
    
    if user:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        
        # TODO: Store reset token with expiry
        # TODO: Send reset email in background
        # background_tasks.add_task(send_password_reset_email, user.email, reset_token)
        pass
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    Refresh access token.
    """
    access_token = create_access_token(
        data={
            "sub": current_user.email,
            "user_id": str(current_user.id)
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRATION_HOURS * 3600
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout user.
    
    Note: With JWT, logout is typically handled client-side by
    deleting the token. This endpoint is provided for consistency.
    """
    # TODO: Add token to blacklist if implementing token revocation
    return {"message": "Successfully logged out"}
