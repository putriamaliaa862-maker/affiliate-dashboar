"""
Bonus rate management routes (Admin only)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from app.database import get_db
from app.models.bonus_rate_rule import BonusRateRule
from app.models.shift_template import ShiftTemplate
from app.models.shopee_account import ShopeeAccount
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.core.permissions import FULL_ACCESS_ROLES

router = APIRouter()


# Schemas
class BonusRateRuleResponse(BaseModel):
    id: int
    shop_id: Optional[int]
    shop_name: str
    day_type: str
    shift_id: int
    shift_name: str
    bonus_per_order: int
    is_active: bool


class BonusRateUpsert(BaseModel):
    shop_id: Optional[int] = None
    day_type: str  # 'weekday', 'weekend', 'all'
    shift_id: int
    bonus_per_order: int
    is_active: bool = True


class BonusRateUpdate(BaseModel):
    is_active: bool


@router.get("/rates", response_model=List[BonusRateRuleResponse])
async def get_bonus_rates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all bonus rate rules
    
    **Permissions:** Admin, Owner, Leader, Partner, Supervisor
    """
    # Allow read access for Leader as well (as per request)
    ALLOWED_READ_ROLES = FULL_ACCESS_ROLES + ["leader"]
    
    if current_user.role not in ALLOWED_READ_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden")

    rules = db.query(BonusRateRule).all()
    
    result = []
    for rule in rules:
        shift = db.query(ShiftTemplate).filter(ShiftTemplate.id == rule.shift_id).first()
        
        shop_name = "Semua Akun"
        if rule.shop_id:
            shop = db.query(ShopeeAccount).filter(ShopeeAccount.id == rule.shop_id).first()
            shop_name = shop.account_name if shop else f"Shop #{rule.shop_id}"
        
        result.append(BonusRateRuleResponse(
            id=rule.id,
            shop_id=rule.shop_id,
            shop_name=shop_name,
            day_type=rule.day_type,
            shift_id=rule.shift_id,
            shift_name=shift.name if shift else f"Shift #{rule.shift_id}",
            bonus_per_order=rule.bonus_per_order,
            is_active=rule.is_active
        ))
    
    return result


@router.post("/rates/upsert", response_model=dict)
async def upsert_bonus_rate(
    data: BonusRateUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create or update bonus rate rule
    
    **Permissions:** Super Admin, Admin, Owner, Supervisor
    """
    # Restrict write access
    ALLOWED_WRITE_ROLES = ["super_admin", "admin", "owner", "supervisor"]
    
    if current_user.role not in ALLOWED_WRITE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Tidak punya akses mengubah bonus rate"
        )
    
    # Validate shift exists
    shift = db.query(ShiftTemplate).filter(ShiftTemplate.id == data.shift_id).first()
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shift with ID {data.shift_id} not found"
        )
    
    # Validate shop if provided
    if data.shop_id:
        shop = db.query(ShopeeAccount).filter(ShopeeAccount.id == data.shop_id).first()
        if not shop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shop with ID {data.shop_id} not found"
            )
    
    # Validate day_type
    if data.day_type not in ['weekday', 'weekend', 'all']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="day_type must be 'weekday', 'weekend', or 'all'"
        )
    
    # Check if rule exists
    existing = db.query(BonusRateRule).filter(
        BonusRateRule.shop_id == data.shop_id,
        BonusRateRule.day_type == data.day_type,
        BonusRateRule.shift_id == data.shift_id
    ).first()
    
    if existing:
        # Update
        existing.bonus_per_order = data.bonus_per_order
        existing.is_active = data.is_active
        db.commit()
        
        return {
            "action": "updated",
            "message": "Aturan bonus berhasil diperbarui",
            "rule_id": existing.id
        }
    else:
        # Create
        new_rule = BonusRateRule(
            shop_id=data.shop_id,
            day_type=data.day_type,
            shift_id=data.shift_id,
            bonus_per_order=data.bonus_per_order,
            is_active=data.is_active
        )
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        
        return {
            "action": "created",
            "message": "Aturan bonus berhasil dibuat",
            "rule_id": new_rule.id
        }


@router.patch("/rates/{rule_id}", response_model=dict)
async def update_bonus_rate_status(
    rule_id: int,
    data: BonusRateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Enable/disable bonus rate rule
    
    **Permissions:** Super Admin, Admin, Owner, Supervisor
    """
    ALLOWED_WRITE_ROLES = ["super_admin", "admin", "owner", "supervisor"]
    
    if current_user.role not in ALLOWED_WRITE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Tidak punya akses mengubah bonus rate"
        )

    rule = db.query(BonusRateRule).filter(BonusRateRule.id == rule_id).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bonus rule with ID {rule_id} not found"
        )
    
    rule.is_active = data.is_active
    db.commit()
    
    status_text = "diaktifkan" if data.is_active else "dinonaktifkan"
    
    return {
        "message": f"Aturan bonus berhasil {status_text}",
        "rule_id": rule.id,
        "is_active": rule.is_active
    }
