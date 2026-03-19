from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timedelta
from typing import Dict, Any
from app.models import UserLogin, UserCreate, UserResponse, AuthToken, SuccessResponse, ErrorResponse
from app.data import get_user_by_email, get_user_by_id, MOCK_USERS, MOCK_TOPICS, create_user, get_mock_test_integrity_status
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

    integrity_status = get_mock_test_integrity_status(user["id"])
    if integrity_status["isSuspended"]:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "message": "Your account is suspended for 2 hours because of repeated mock test violations.",
                "suspendedUntil": integrity_status["suspendedUntil"],
                "warnings": integrity_status["warnings"],
                "maxWarnings": integrity_status["maxWarnings"],
            },
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": user["id"]}, 
        expires_delta=access_token_expires
    )
    
    # Prepare user response (without password)
    user_data = {k: v for k, v in user.items() if k != "password"}
    user_data.setdefault("antiCheatWarnings", 0)
    user_data.setdefault("suspendedUntil", None)
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
    
    # Create new user via data layer (persists to MongoDB)
    hashed_password = auth_utils.get_password_hash(user_data.password)
    new_user_id = create_user(user_data.email, user_data.name, hashed_password)
    new_user = MOCK_USERS[new_user_id]
    
    # Generate access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": new_user_id},
        expires_delta=access_token_expires
    )
    
    # Prepare user response (without password)
    user_resp = {k: v for k, v in new_user.items() if k != "password"}
    user_resp.setdefault("antiCheatWarnings", 0)
    user_resp.setdefault("suspendedUntil", None)
    user_resp.setdefault("createdAt", None)
    user_resp.setdefault("updatedAt", None)
    user_response = UserResponse(**user_resp)
    
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
    user_data.setdefault("antiCheatWarnings", 0)
    user_data.setdefault("suspendedUntil", None)
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
    user_data.setdefault("antiCheatWarnings", 0)
    user_data.setdefault("suspendedUntil", None)
    user_data.setdefault("createdAt", None)
    user_data.setdefault("updatedAt", None)
    user_response = UserResponse(**user_data)
    
    return AuthToken(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )