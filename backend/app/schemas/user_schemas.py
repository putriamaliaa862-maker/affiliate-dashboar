"""
User schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    role: str = Field(..., description="User role: super_admin, admin, leader, affiliate")
    leader_id: Optional[int] = Field(None, description="Leader user ID for affiliate role")
    
    @validator('role')
    def validate_role(cls, v):
        # Normalize: "Super Admin" -> "super_admin"
        normalized = v.strip().lower().replace(" ", "_").replace("-", "_")
        allowed_roles = ['super_admin', 'admin', 'leader', 'affiliate', 'owner', 'supervisor', 'partner', 'host']
        if normalized not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return normalized


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('leader_id')
    def validate_leader_for_affiliate(cls, v, values):
        if values.get('role') == 'affiliate' and not v:
            raise ValueError('Affiliate role requires a leader_id')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user (all fields optional)"""
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = None
    leader_id: Optional[int] = None
    is_active: Optional[bool] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v is not None:
            allowed_roles = ['super_admin', 'admin', 'leader', 'affiliate', 'owner', 'supervisor', 'partner', 'host']
            if v not in allowed_roles:
                raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v


class ChangePasswordRequest(BaseModel):
    """Schema for changing password"""
    current_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    role: str
    leader_id: Optional[int]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for paginated user list"""
    users: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
