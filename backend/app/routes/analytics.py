from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import Optional, List
from datetime import datetime, date, time as dt_time
from pydantic import BaseModel

from app.database import get_db
from app.models.order import Order
from app.models.shopee_account import ShopeeAccount
from app.models.shift_template import ShiftTemplate
from app.models.bonus_rate_rule import BonusRateRule
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.core.permissions import verify_financial_access, apply_scope_restriction

router = APIRouter()


# Schemas
class HourlyData(BaseModel):
    hour: str
    total_orders: int
    total_gmv: float
    total_commission: float


class ShiftData(BaseModel):
    shift_id: int
    shift_name: str
    start_time: str
    end_time: str
    total_orders: int
    total_gmv: float
    total_commission: float


class ShiftBonus(BaseModel):
    shift_id: int
    shift_name: str
    total_orders: int
    bonus_per_order: int
    bonus_amount: int


class BonusShiftResponse(BaseModel):
    date: str
    day_type: str
    shop_id: Optional[int]
    host_id: Optional[int]
    shift_results: List[ShiftBonus]
    total_bonus: int


class HostShiftBreakdown(BaseModel):
    shift_name: str
    orders: int
    bonus: int


class HostLeaderboardItem(BaseModel):
    rank: int
    host_id: int
    host_name: str
    total_orders: int
    total_gmv: float
    total_commission: float
    total_bonus: int
    shift_breakdown: List[HostShiftBreakdown]


class LeaderboardResponse(BaseModel):
    date: str
    shop_id: Optional[int]
    leaderboard: List[HostLeaderboardItem]


# Helper functions
def get_day_type(target_date: date) -> str:
    """Determine if date is weekday or weekend"""
    # 5 = Saturday, 6 = Sunday
    weekday_num = target_date.weekday()
    return "weekend" if weekday_num >= 5 else "weekday"


def resolve_bonus_rate(db: Session, shop_id: Optional[int], day_type: str, shift_id: int) -> int:
    """
    Resolve bonus rate using priority matching:
    1. shop_id match + day_type match
    2. shop_id match + day_type = 'all'
    3. shop_id NULL + day_type match
    4. shop_id NULL + day_type = 'all'
    """
    # Try exact match
    rule = db.query(BonusRateRule).filter(
        BonusRateRule.shop_id == shop_id,
        BonusRateRule.day_type == day_type,
        BonusRateRule.shift_id == shift_id,
        BonusRateRule.is_active == True
    ).first()
    if rule:
        return rule.bonus_per_order
    
    # Try shop match with 'all' day
    if shop_id is not None:
        rule = db.query(BonusRateRule).filter(
            BonusRateRule.shop_id == shop_id,
            BonusRateRule.day_type == 'all',
            BonusRateRule.shift_id == shift_id,
            BonusRateRule.is_active == True
        ).first()
        if rule:
            return rule.bonus_per_order
    
    # Try global with day_type match
    rule = db.query(BonusRateRule).filter(
        BonusRateRule.shop_id == None,
        BonusRateRule.day_type == day_type,
        BonusRateRule.shift_id == shift_id,
        BonusRateRule.is_active == True
    ).first()
    if rule:
        return rule.bonus_per_order
    
    # Fallback to global 'all'
    rule = db.query(BonusRateRule).filter(
        BonusRateRule.shop_id == None,
        BonusRateRule.day_type == 'all',
        BonusRateRule.shift_id == shift_id,
        BonusRateRule.is_active == True
    ).first()
    
    return rule.bonus_per_order if rule else 0


def get_shift_for_time(db: Session, order_time: datetime) -> Optional[ShiftTemplate]:
    """Determine which shift an order belongs to"""
    order_hour = order_time.time()
    
    shifts = db.query(ShiftTemplate).filter(ShiftTemplate.is_active == True).all()
    
    for shift in shifts:
        # Handle shift crossing midnight
        if shift.end_time < shift.start_time:  # e.g., 20:00 to 00:00
            if order_hour >= shift.start_time or order_hour < shift.end_time:
                return shift
        else:
            if shift.start_time <= order_hour < shift.end_time:
                return shift
    
    return None


# Endpoints
@router.get("/orders-hourly", response_model=List[HourlyData])
async def get_hourly_orders(
    date: date = Query(..., description="Date in YYYY-MM-DD"),
    shop_id: Optional[int] = None,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get hourly order breakdown for 05:00-23:00 WIB
    """
    if not verify_financial_access(current_user, "orders-hourly"):
        raise HTTPException(status_code=403, detail="Forbidden")

    # Build query
    query = db.query(
        extract('hour', Order.date).label('hour'),
        func.count(Order.id).label('total_orders'),
        func.sum(Order.total_amount).label('total_gmv'),
        func.sum(Order.commission_amount).label('total_commission')
    ).filter(
        func.date(Order.date) == date,
        Order.status == 'completed'
    )
    
    # Apply RBAC Scope
    query = apply_scope_restriction(query, current_user, Order)

    if shop_id:
        query = query.filter(Order.shopee_account_id == shop_id)
    
    # TODO: Add host_id filter when orders have host relationship
    
    query = query.group_by(extract('hour', Order.date))
    
    results = query.all()
    
    # Create full 05:00-23:00 range
    hourly_data = {}
    for hour in range(5, 24):  # 5 to 23
        hourly_data[hour] = {
            "hour": f"{hour:02d}:00",
            "total_orders": 0,
            "total_gmv": 0.0,
            "total_commission": 0.0
        }
    
    # Fill in actual data
    for row in results:
        hour = int(row.hour)
        if 5 <= hour <= 23:
            hourly_data[hour] = {
                "hour": f"{hour:02d}:00",
                "total_orders": row.total_orders or 0,
                "total_gmv": float(row.total_gmv or 0),
                "total_commission": float(row.total_commission or 0)
            }
    
    return [HourlyData(**data) for hour, data in sorted(hourly_data.items())]


@router.get("/orders-shift", response_model=List[ShiftData])
async def get_shift_orders(
    date: date = Query(...),
    shop_id: Optional[int] = None,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get orders grouped by shift
    """
    if not verify_financial_access(current_user, "orders-shift"):
        raise HTTPException(status_code=403, detail="Forbidden")

    # Get all orders for the date
    query = db.query(Order).filter(
        func.date(Order.date) == date,
        Order.status == 'completed'
    )
    
    # Apply RBAC Scope
    query = apply_scope_restriction(query, current_user, Order)

    if shop_id:
        query = query.filter(Order.shopee_account_id == shop_id)
    
    orders = query.all()
    
    # Group by shift
    shifts = db.query(ShiftTemplate).filter(ShiftTemplate.is_active == True).order_by(ShiftTemplate.id).all()
    
    shift_data = []
    for shift in shifts:
        shift_orders = [o for o in orders if get_shift_for_time(db, o.date) and get_shift_for_time(db, o.date).id == shift.id]
        
        total_orders = len(shift_orders)
        total_gmv = sum(float(o.total_amount or 0) for o in shift_orders)
        total_commission = sum(float(o.commission_amount or 0) for o in shift_orders)
        
        shift_data.append(ShiftData(
            shift_id=shift.id,
            shift_name=shift.name,
            start_time=shift.start_time.strftime("%H:%M"),
            end_time=shift.end_time.strftime("%H:%M"),
            total_orders=total_orders,
            total_gmv=total_gmv,
            total_commission=total_commission
        ))
    
    return shift_data


@router.get("/bonus-shift", response_model=BonusShiftResponse)
async def get_bonus_shift(
    date: date = Query(...),
    shop_id: Optional[int] = None,
    host_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate bonus per shift based on rates
    """
    # Reuse permissions from get_shift_orders implicitly or explicit check?
    # Better explicit
    if not verify_financial_access(current_user, "bonus-shift"):
        raise HTTPException(status_code=403, detail="Forbidden")

    day_type = get_day_type(date)
    
    # Get shift order counts (Note: calling endpoint function directly bypasses Depends, 
    # but we already did permission check above)
    # However, get_shift_orders expects params. We can just reuse logic or call function carefully.
    # Calling async function directly:
    shift_orders_data = await get_shift_orders(date, shop_id, host_id, db, current_user)
    
    shift_results = []
    total_bonus = 0
    
    for shift_data in shift_orders_data:
        # Resolve bonus rate
        bonus_per_order = resolve_bonus_rate(db, shop_id, day_type, shift_data.shift_id)
        bonus_amount = shift_data.total_orders * bonus_per_order
        total_bonus += bonus_amount
        
        shift_results.append(ShiftBonus(
            shift_id=shift_data.shift_id,
            shift_name=shift_data.shift_name,
            total_orders=shift_data.total_orders,
            bonus_per_order=bonus_per_order,
            bonus_amount=bonus_amount
        ))
    
    return BonusShiftResponse(
        date=str(date),
        day_type=day_type,
        shop_id=shop_id,
        host_id=host_id,
        shift_results=shift_results,
        total_bonus=total_bonus
    )


@router.get("/bonus-host-leaderboard", response_model=LeaderboardResponse)
async def get_bonus_leaderboard(
    date: date = Query(...),
    shop_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get host leaderboard ranked by total bonus
    """
    if not verify_financial_access(current_user, "bonus-host-leaderboard"):
        raise HTTPException(status_code=403, detail="Forbidden")

    # For now, return sample structure
    # TODO: Implement actual host aggregation when orders have host_id
    
    return LeaderboardResponse(
        date=str(date),
        shop_id=shop_id,
        leaderboard=[]  # Empty until host relationship exists
    )
