from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timedelta
from typing import Dict, Any
from app.models import UserLogin, UserCreate, UserResponse, AuthToken, SuccessResponse, ErrorResponse
from app.data import get_user_by_email, get_user_by_id, MOCK_USERS
from app.core.auth import auth_utils, get_current_user_from_token
from app.core.config import settings
import uuid

router = APIRouter()

@router.post("/login", response_model=AuthToken)
async def login(credentials: UserLogin):
    """Authenticate user with email and password"""
    user = get_user_by_email(credentials.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not auth_utils.verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": user["id"]}, 
        expires_delta=access_token_expires
    )
    
    # Prepare user response (without password)
    user_data = {k: v for k, v in user.items() if k != "password"}
    user_data.setdefault("createdAt", None)
    user_data.setdefault("updatedAt", None)
    user_response = UserResponse(**user_data)
    
    return AuthToken(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user=user_response
    )

@router.post("/signup", response_model=AuthToken)
async def signup(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    if get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    # Create new user with hashed password
    new_user_id = str(uuid.uuid4())
    hashed_password = auth_utils.get_password_hash(user_data.password)
    
    new_user = {
        "id": new_user_id,
        "name": user_data.name,
        "email": user_data.email,
        "password": hashed_password,
        "completedTopics": [],
        "pendingTopics": ["topic-1", "topic-2"],
        "inProgressTopics": [],
        "videosWatched": [],
        "totalScore": 0,
        "rank": len(MOCK_USERS) + 1,
        "preferredStyle": "visual",
        "confusionCount": 0,
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
    
    MOCK_USERS[new_user_id] = new_user
    
    # Generate access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": new_user_id},
        expires_delta=access_token_expires
    )
    
    # Prepare user response (without password)
    user_data = {k: v for k, v in new_user.items() if k != "password"}
    user_response = UserResponse(**user_data)
    
    return AuthToken(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )

@router.post("/logout", response_model=SuccessResponse)
async def logout(current_user: dict = Depends(get_current_user_from_token)):
    """Logout user (invalidate token on client side)"""
    return SuccessResponse(
        success=True,
        message="Logged out successfully"
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: dict = Depends(get_current_user_from_token)):
    """Get current authenticated user"""
    # Return user without password
    user_data = {k: v for k, v in current_user.items() if k != "password"}
    user_data.setdefault("createdAt", None)
    user_data.setdefault("updatedAt", None)
    return UserResponse(**user_data)

@router.post("/refresh", response_model=AuthToken)
async def refresh_token(current_user: dict = Depends(get_current_user_from_token)):
    """Refresh access token"""
    user = current_user
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": user["id"]},
        expires_delta=access_token_expires
    )
    
    # Prepare user response
    user_data = {k: v for k, v in user.items() if k != "password"}
    user_data.setdefault("createdAt", None)
    user_data.setdefault("updatedAt", None)
    user_response = UserResponse(**user_data)
    
    return AuthToken(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )