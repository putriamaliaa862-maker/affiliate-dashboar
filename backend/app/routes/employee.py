"""
Employee management routes with RBAC
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.employee import Employee
from app.models.studio import Studio
from app.models.user import User
from app.models.activity_log import ActivityLog
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Create a new employee.
    
    **Permissions:** Admin or Super Admin
    
    - **studio_id**: Studio this employee belongs to
    - **name**: Employee full name
    - **email**: Unique email address
    - **role**: host, leader, supervisor, or director
    - **salary_base**: Base salary (optional)
    - **hire_date**: Date of hiring (optional)
    """
    # Validate studio exists
    studio = db.query(Studio).filter(Studio.id == employee_data.studio_id).first()
    if not studio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Studio with ID {employee_data.studio_id} not found"
        )
    
    # Check if email already exists
    existing = db.query(Employee).filter(Employee.email == employee_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create employee
    db_employee = Employee(
        **employee_data.dict()
    )
    
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="create_employee",
        entity_type="employee",
        entity_id=db_employee.id,
        new_value={"name": db_employee.name, "role": db_employee.role},
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    return db_employee


@router.get("", response_model=List[EmployeeResponse])
async def list_employees(
    studio_id: Optional[int] = Query(None, description="Filter by studio ID"),
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all employees with filtering and pagination.
    
    **Permissions:** Any authenticated user
    """
    query = db.query(Employee)
    
    # Apply filters
    if studio_id is not None:
        query = query.filter(Employee.studio_id == studio_id)
    
    if role is not None:
        query = query.filter(Employee.role == role)
    
    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)
    
    employees = query.offset(skip).limit(limit).all()
    return employees


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get employee by ID.
    
    **Permissions:** Any authenticated user
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Update employee information.
    
    **Permissions:** Admin or Super Admin
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    # Store old values for logging
    old_values = {
        "name": employee.name,
        "email": employee.email,
        "role": employee.role
    }
    
    # Update fields
    update_data = employee_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)
    
    db.commit()
    db.refresh(employee)
    
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="update_employee",
        entity_type="employee",
        entity_id=employee.id,
        old_value=old_values,
        new_value={"name": employee.name, "email": employee.email, "role": employee.role},
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    return employee


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Soft delete employee (set is_active = False).
    
    **Permissions:** Admin or Super Admin
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    # Soft delete
    employee.is_active = False
    db.commit()
    
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="delete_employee",
        entity_type="employee",
        entity_id=employee.id,
        old_value={"is_active": True},
        new_value={"is_active": False},
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    return {"message": f"Employee {employee.name} deleted successfully"}
