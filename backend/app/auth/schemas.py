"""
Pydantic schemas for authentication and user management.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    LEADER = "leader"
    AFFILIATE = "affiliate"
    OWNER = "owner"
    SUPERVISOR = "supervisor"
    PARTNER = "partner"
    HOST = "host"


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole
    leader_id: Optional[int] = None
    
    @validator('role', pre=True)
    def normalize_role(cls, v):
        if isinstance(v, str):
            return v.strip().lower().replace(" ", "_").replace("-", "_")
        return v

    @validator('leader_id')
    def validate_leader_for_affiliate(cls, v, values):
        """Affiliates must have a leader assigned"""
        # Note: role here is already validated/converted to Enum member if successful
        if values.get('role') == UserRole.AFFILIATE and v is None:
            raise ValueError('Affiliates must have a leader assigned')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    leader_id: Optional[int] = None
    is_active: Optional[bool] = None

    @validator('role', pre=True)
    def normalize_role(cls, v):
        if isinstance(v, str):
            return v.strip().lower().replace(" ", "_").replace("-", "_")
        return v


class UserChangePassword(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    role: str
    leader_id: Optional[int]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserWithTeam(UserResponse):
    """User response with team information"""
    team_members: list[UserResponse] = []


class LoginRequest(BaseModel):
    """Login credentials"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class AssignLeaderRequest(BaseModel):
    """Schema for assigning leader to affiliate"""
    leader_id: int
