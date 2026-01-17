"""
User management routes for CRUD operations.
Implements role-based access control.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.activity_log import ActivityLog
from app.auth.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithTeam,
    UserChangePassword,
    AssignLeaderRequest
)
from app.auth.jwt import get_password_hash, verify_password
from app.auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/users", tags=["User Management"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Create a new user.
    
    **Permissions:** Admin or Super Admin
    
    - **username**: Unique username
    - **email**: Unique email
    - **password**: Minimum 8 characters
    - **role**: super_admin, admin, leader, or affiliate
    - **leader_id**: Required for affiliates
    """
    # Check if username or email already exists
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Validate leader_id if provided
    if user_data.leader_id:
        leader = db.query(User).filter(User.id == user_data.leader_id).first()
        if not leader:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leader not found"
            )
        if leader.role not in ['leader', 'admin', 'super_admin']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned leader must have leader, admin, or super_admin role"
            )
    
    # Create user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role,
        leader_id=user_data.leader_id
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="create_user",
        entity_type="user",
        entity_id=new_user.id,
        new_value={"username": new_user.username, "role": new_user.role},
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    return new_user.to_dict()


@router.get("", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("leader"))
):
    """
    List all users with filtering and pagination.
    
    **Permissions:** Leader or higher
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **role**: Filter by role
    - **is_active**: Filter by active status
    - **search**: Search in username, email, full_name
    """
    query = db.query(User)
    
    # Apply filters
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.username.ilike(search_pattern)) |
            (User.email.ilike(search_pattern)) |
            (User.full_name.ilike(search_pattern))
        )
    
    # Role-based filtering
    if current_user.role == "leader":
        # Leaders can only see their team members + themselves
        query = query.filter(
            (User.leader_id == current_user.id) | (User.id == current_user.id)
        )
    
    users = query.offset(skip).limit(limit).all()
    return [user.to_dict() for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user by ID.
    
    **Permissions:** 
    - Admins: Can view any user
    - Leaders: Can view own team members
    - Affiliates: Can view only themselves
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check access permissions
    if current_user.role not in ['super_admin', 'admin']:
        if current_user.role == 'leader':
            # Leaders can view their team members
            if user.leader_id != current_user.id and user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        elif current_user.id != user_id:
            # Affiliates can only view themselves
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return user.to_dict()


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Update user information.
    
    **Permissions:** Admin or Super Admin
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Store old values for logging
    old_values = user.to_dict()
    
    # Update fields
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="update_user",
        entity_type="user",
        entity_id=user.id,
        old_value=old_values,
        new_value=user.to_dict(),
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    return user.to_dict()


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin"))
):
    """
    Soft delete user (set is_active = False).
    
    **Permissions:** Super Admin only
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    # Soft delete
    user.is_active = False
    db.commit()
    
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="delete_user",
        entity_type="user",
        entity_id=user.id,
        old_value={"is_active": True},
        new_value={"is_active": False},
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/change-password")
async def change_password(
    user_id: int,
    password_data: UserChangePassword,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change user password.
    
    Users can change their own password.
    Admins can change any password.
    """
    # Check permissions
    if current_user.id != user_id and current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password if user is changing own password
    if current_user.id == user_id:
        if not verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
    
    # Update password
    user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="change_password",
        entity_type="user",
        entity_id=user.id,
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/leaders/list", response_model=List[UserResponse])
async def list_leaders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Get list of all leaders for assignment.
    
    **Permissions:** Admin or higher
    """
    leaders = db.query(User).filter(
        User.role.in_(['leader', 'admin', 'super_admin']),
        User.is_active == True
    ).all()
    
    return [leader.to_dict() for leader in leaders]


@router.post("/{affiliate_id}/assign-leader")
async def assign_leader(
    affiliate_id: int,
    assignment: AssignLeaderRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Assign or change leader for an affiliate.
    
    **Permissions:** Admin or higher
    """
    affiliate = db.query(User).filter(User.id == affiliate_id).first()
    
    if not affiliate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Affiliate not found"
        )
    
    if affiliate.role != "affiliate":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an affiliate"
        )
    
    leader = db.query(User).filter(User.id == assignment.leader_id).first()
    
    if not leader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leader not found"
        )
    
    if leader.role not in ['leader', 'admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assigned user must be a leader or admin"
        )
    
    # Update assignment
    old_leader_id = affiliate.leader_id
    affiliate.leader_id = assignment.leader_id
    db.commit()
    
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="assign_leader",
        entity_type="user",
        entity_id=affiliate.id,
        old_value={"leader_id": old_leader_id},
        new_value={"leader_id": assignment.leader_id},
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    return {"message": "Leader assigned successfully"}


@router.get("/{leader_id}/team", response_model=List[UserResponse])
async def get_team_members(
    leader_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all team members for a leader.
    
    **Permissions:** 
    - Leaders can view their own team
    - Admins can view any team
    """
    # Check permissions
    if current_user.role not in ['admin', 'super_admin'] and current_user.id != leader_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    team_members = db.query(User).filter(
        User.leader_id == leader_id,
        User.is_active == True
    ).all()
    
    return [member.to_dict() for member in team_members]
