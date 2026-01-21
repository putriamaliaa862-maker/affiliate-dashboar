"""
Authentication routes for login, registration, and token management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.activity_log import ActivityLog
from app.auth.schemas import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse
)
from app.auth.jwt import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.
    
    - **username**: Username or email
    - **password**: User password
    
    Returns access token and refresh token.
    """
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == credentials.username) | (User.email == credentials.username)
    ).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        # Log failed login attempt
        if user:
            log = ActivityLog(
                user_id=user.id,
                action="login_failed",
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )
            db.add(log)
            db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    token_data = {
        "sub": str(user.id),  # Convert to string per JWT standard
        "username": user.username,
        "role": user.role
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Log successful login
    log = ActivityLog(
        user_id=user.id,
        action="login_success",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    db.add(log)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    """
    payload = verify_token(refresh_request.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    
    # Convert string sub to integer
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    token_data = {
        "sub": str(user.id),  # Convert to string per JWT standard
        "username": user.username,
        "role": user.role
    }
    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user (client should delete tokens).
    Logs the logout activity.
    """
    log = ActivityLog(
        user_id=current_user.id,
        action="logout",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    db.add(log)
    db.commit()
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    """
    return current_user.to_dict()


# ==================== ACCESS CODE MANAGEMENT ====================

def generate_access_code() -> str:
    """
    Generate a unique access code in format: XXXX-XXXX-XXXX
    Uses uppercase alphanumeric characters (excluding confusing ones like O, 0, I, 1)
    """
    import random
    import string
    
    # Character set (exclude confusing chars)
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    
    # Generate 3 segments of 4 characters each
    segments = []
    for _ in range(3):
        segment = ''.join(random.choice(chars) for _ in range(4))
        segments.append(segment)
    
    return '-'.join(segments)


@router.post("/access-code/regenerate")
async def regenerate_access_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate or regenerate access code for current user.
    Access code is used for extension authentication.
    
    Returns the new access code.
    """
    max_attempts = 10
    for attempt in range(max_attempts):
        new_code = generate_access_code()
        
        # Check uniqueness
        existing = db.query(User).filter(User.access_code == new_code).first()
        if not existing:
            # Update current user's access code
            current_user.access_code = new_code
            db.commit()
            db.refresh(current_user)
            
            # Log activity
            log = ActivityLog(
                user_id=current_user.id,
                action="access_code_regenerated",
                entity_type="user",
                entity_id=current_user.id
            )
            db.add(log)
            db.commit()
            
            return {
                "access_code": new_code,
                "message": "Access code generated successfully"
            }
    
    # Unlikely to reach here, but handle it
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to generate unique access code. Please try again."
    )


@router.get("/access-code/me")
async def get_my_access_code(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's access code.
    Returns null if not yet generated.
    """
    return {
        "access_code": current_user.access_code,
        "has_code": current_user.access_code is not None
    }
