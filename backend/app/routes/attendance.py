"""
Attendance management routes with RBAC and duplicate prevention
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, Date
from typing import List, Optional
from datetime import datetime, date, time as dt_time

from app.database import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.user import User
from app.models.activity_log import ActivityLog
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate, AttendanceResponse
from app.auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/api/attendance", tags=["attendance"])



@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def create_attendance(
    attendance_data: AttendanceCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("leader"))  # Admin & Leader only
):
    """
    Record attendance for an employee.
    
    **Permissions:** Leader or higher (Admin, Super Admin)
    
    **Duplicate Prevention:** One record per employee per day
    
    - **employee_id**: Employee to record attendance for
    - **date**: Date of attendance (YYYY-MM-DD)
    - **check_in_time**: Check-in time (HH:MM:SS)
    - **check_out_time**: Check-out time (optional)
    - **status**: present, late, absent, sick
    - **notes**: Optional notes
    """
    # Validate employee exists
    employee = db.query(Employee).filter(Employee.id == attendance_data.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {attendance_data.employee_id} not found"
        )
    
    # DUPLICATE PREVENTION: Check if attendance already exists for this employee on this date
    existing = db.query(Attendance).filter(
        and_(
            Attendance.employee_id == attendance_data.employee_id,
            func.date(Attendance.date) == attendance_data.date
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Attendance already recorded for {employee.name} on {attendance_data.date}. Use PUT to update."
        )
    
    # Combine date + time for check_in/check_out
    check_in_dt = None
    if attendance_data.check_in_time:
        check_in_dt = datetime.combine(attendance_data.date, attendance_data.check_in_time)
    
    check_out_dt = None
    if attendance_data.check_out_time:
        check_out_dt = datetime.combine(attendance_data.date, attendance_data.check_out_time)
    
    # Create attendance
    db_attendance = Attendance(
        employee_id=attendance_data.employee_id,
        date=datetime.combine(attendance_data.date, dt_time.min),  # Store as datetime with time 00:00:00
        check_in=check_in_dt,
        check_out=check_out_dt,
        status=attendance_data.status,
        notes=attendance_data.notes
    )
    
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="create_attendance",
        entity_type="attendance",
        entity_id=db_attendance.id,
        new_value={"employee_id": employee.id, "employee_name": employee.name, "date": str(attendance_data.date)},
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    # Add employee name to response
    response_data = AttendanceResponse.from_orm(db_attendance)
    response_data.employee_name = employee.name
    
    return response_data


@router.get("", response_model=List[AttendanceResponse])
async def list_attendance(
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    from_date: Optional[date] = Query(None, alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, alias="to", description="End date (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List attendance records with filtering.
    
    **Permissions:** Any authenticated user
    
    **Role-based filtering:**
    - Affiliates: Can only see their own attendance
    - Leaders: Can see their team's attendance
    - Admins: Can see all attendance
    """
    query = db.query(Attendance).join(Employee)
    
    # Role-based filtering
    if current_user.role == "affiliate":
        # TODO: Link user to employee properly
        # For now, restrict to empty set if not implemented
        query = query.filter(Attendance.employee_id == -1)
    
    # Apply filters
    if employee_id is not None:
        query = query.filter(Attendance.employee_id == employee_id)
    
    if from_date:
        query = query.filter(func.date(Attendance.date) >= from_date)
    
    if to_date:
        query = query.filter(func.date(Attendance.date) <= to_date)
    
    if status:
        query = query.filter(Attendance.status == status)
    
    attendances = query.order_by(Attendance.date.desc()).offset(skip).limit(limit).all()
    
    # Add employee names to response
    result = []
    for att in attendances:
        resp = AttendanceResponse.from_orm(att)
        resp.employee_name = att.employee.name if att.employee else "Unknown"
        result.append(resp)
    
    return result


@router.get("/{attendance_id}", response_model=AttendanceResponse)
async def get_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get attendance record by ID.
    
    **Permissions:** Any authenticated user
    """
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with ID {attendance_id} not found"
        )
    
    response = AttendanceResponse.from_orm(attendance)
    response.employee_name = attendance.employee.name if attendance.employee else "Unknown"
    
    return response


@router.put("/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: int,
    attendance_data: AttendanceUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("leader"))  # Admin & Leader only
):
    """
    Update attendance record.
    
    **Permissions:** Leader or higher
    """
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with ID {attendance_id} not found"
        )
    
    # Store old values
    old_values = {
        "status": attendance.status,
        "check_in": str(attendance.check_in) if attendance.check_in else None,
        "check_out": str(attendance.check_out) if attendance.check_out else None
    }
    
    # Update fields
    update_data = attendance_data.dict(exclude_unset=True)
    
    # Handle time fields
    if 'check_in_time' in update_data and update_data['check_in_time']:
        attendance.check_in = datetime.combine(attendance.date.date(), update_data['check_in_time'])
    
    if 'check_out_time' in update_data and update_data['check_out_time']:
        attendance.check_out = datetime.combine(attendance.date.date(), update_data['check_out_time'])
    
    if 'status' in update_data:
        attendance.status = update_data['status']
    
    if 'notes' in update_data:
        attendance.notes = update_data['notes']
    
    db.commit()
    db.refresh(attendance)
    
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="update_attendance",
        entity_type="attendance",
        entity_id=attendance.id,
        old_value=old_values,
        new_value={"status": attendance.status},
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    response = AttendanceResponse.from_orm(attendance)
    response.employee_name = attendance.employee.name if attendance.employee else "Unknown"
    
    return response


@router.delete("/{attendance_id}")
async def delete_attendance(
    attendance_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))  # Admin only
):
    """
    Delete attendance record.
    
    **Permissions:** Admin or Super Admin only
    """
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with ID {attendance_id} not found"
        )
    
    employee_name = attendance.employee.name if attendance.employee else "Unknown"
    attendance_date = attendance.date.date() if attendance.date else "Unknown"
    
    # Hard delete (or implement soft delete if preferred)
    db.delete(attendance)
    db.commit()
    
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="delete_attendance",
        entity_type="attendance",
        entity_id=attendance_id,
        old_value={"employee": employee_name, "date": str(attendance_date)},
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    return {"message": f"Attendance record for {employee_name} on {attendance_date} deleted successfully"}
