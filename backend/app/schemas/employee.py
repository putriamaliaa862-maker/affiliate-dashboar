"""
Pydantic schemas for Employee management
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class EmployeeBase(BaseModel):
    """Base employee schema"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    role: str = Field(..., description="host, leader, supervisor, director")
    salary_base: Optional[Decimal] = Field(default=0, ge=0)
    hire_date: Optional[date] = None
    
    @validator('role')
    def validate_role(cls, v):
        """Validate employee role"""
        valid_roles = ['host', 'leader', 'supervisor', 'director']
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee"""
    studio_id: int = Field(..., gt=0, description="Studio ID this employee belongs to")


class EmployeeUpdate(BaseModel):
    """Schema for updating employee"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[str] = None
    salary_base: Optional[Decimal] = Field(None, ge=0)
    hire_date: Optional[date] = None
    is_active: Optional[bool] = None
    
    @validator('role')
    def validate_role(cls, v):
        """Validate employee role"""
        if v is not None:
            valid_roles = ['host', 'leader', 'supervisor', 'director']
            if v not in valid_roles:
                raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v


class EmployeeResponse(EmployeeBase):
    """Schema for employee response"""
    id: int
    studio_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
