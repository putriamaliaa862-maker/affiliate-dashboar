"""
Pydantic schemas for Attendance management
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date, time


class AttendanceBase(BaseModel):
    """Base attendance schema"""
    employee_id: int = Field(..., gt=0)
    date: date
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    status: str = Field(..., description="present, late, absent, sick")
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('status')
    def validate_status(cls, v):
        """Validate attendance status"""
        valid_statuses = ['present', 'late', 'absent', 'sick']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class AttendanceCreate(AttendanceBase):
    """Schema for creating attendance"""
    pass


class AttendanceUpdate(BaseModel):
    """Schema for updating attendance"""
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    status: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('status')
    def validate_status(cls, v):
        """Validate attendance status"""
        if v is not None:
            valid_statuses = ['present', 'late', 'absent', 'sick']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class AttendanceResponse(AttendanceBase):
    """Schema for attendance response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    # Include employee details
    employee_name: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            time: lambda v: v.isoformat()
        }
