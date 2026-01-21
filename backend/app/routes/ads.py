from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date, datetime, timedelta
from typing import List, Optional

from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.shopee_account import ShopeeAccount
from app.models.order import Order
from app.models.ads import AdsDailySpend, AdsDailyMetrics, AudienceBudgetSetting, AudienceBudgetAction
from app.schemas.ads import (
    AdsCenterAccountRow, SpendUpsertRequest, MetricsUpsertRequest,
    AudienceSettingsUpsertRequest, AudienceAddBudgetRequest, GenericSuccessResponse,
    LogsSpendRow, LogsAudienceRow, LogsRoasRow
)
from app.core.permissions import get_allowed_account_ids

router = APIRouter(prefix="/api/ads", tags=["ads"])

# --- Helper Logic for Boros Score ---
def calculate_boros_status(
    account_spend: int, 
    account_gmv: int, 
    total_spend_all: int, 
    total_gmv_all: int, 
    median_roas: float
):
    if account_spend == 0:
        return 0, "AMAN", "No Spend"

    roas = account_gmv / account_spend if account_spend > 0 else 0
    share_spend = account_spend / total_spend_all if total_spend_all > 0 else 0
    share_gmv = account_gmv / total_gmv_all if total_gmv_all > 0 else 0
    
    score = 0
    reasons = []

    # Rule 1: ROAS Check
    if median_roas > 0 and roas < (median_roas * 0.7):
        score += 40
        reasons.append(f"ROAS {roas:.1f}x jauh dibawah median {median_roas:.1f}x")

    # Rule 2: High Spend Low Impact
    if share_spend > 0.35 and share_gmv < 0.20:
        score += 40
        reasons.append(f"Spend dominan ({share_spend:.0%}) tapi GMV kecil ({share_gmv:.0%})")

    # Status Mapping
    if score >= 60:
        status = "BOROS"
    elif score >= 30:
        status = "WASPADA"
    else:
        status = "AMAN"
        
    reason_str = "; ".join(reasons) if reasons else "Performa Stabil"
    return score, status, reason_str


# --- Endpoints ---

@router.get("/center", response_model=List[AdsCenterAccountRow])
def get_ads_center_data(
    date: date,
    account_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed_ids = get_allowed_account_ids(db, current_user)
    if not allowed_ids:
        return []

    # Filter accounts
    query = db.query(ShopeeAccount).filter(ShopeeAccount.id.in_(allowed_ids), ShopeeAccount.is_active == True)
    if account_id:
        if account_id not in allowed_ids:
            raise HTTPException(status_code=403, detail="Not allowed to access this account")
        query = query.filter(ShopeeAccount.id == account_id)
    accounts = query.all()
    
    # Pre-fetch data for all relevant accounts to calculate totals/median for Boros Score
    # 1. Spend
    spends = db.query(
        AdsDailySpend.shopee_account_id, 
        func.sum(AdsDailySpend.spend_amount).label("total_spend")
    ).filter(
        AdsDailySpend.date == date,
        AdsDailySpend.shopee_account_id.in_(allowed_ids)
    ).group_by(AdsDailySpend.shopee_account_id).all()
    spend_map = {s.shopee_account_id: s.total_spend for s in spends}

    # 2. GMV (from Orders) - Use dedicated date column for accuracy
    # Order model has both created_at and date columns
    # Use date column for business date matching (more accurate)
    # Only count completed orders (exclude cancelled)
    gmvs = db.query(
        Order.shopee_account_id,
        func.sum(Order.total_amount).label("total_gmv")
    ).filter(
        func.date(Order.date) == date,  # Use date column instead of created_at
        Order.shopee_account_id.in_(allowed_ids),
        Order.status == 'completed'  # Only count completed orders
    ).group_by(Order.shopee_account_id).all()
    
    gmv_map = {g.shopee_account_id: g.total_gmv for g in gmvs}

    # 3. Metrics (Manual ROAS)
    metrics = db.query(AdsDailyMetrics).filter(
        AdsDailyMetrics.date == date,
        AdsDailyMetrics.shopee_account_id.in_(allowed_ids)
    ).all()
    metrics_map = {m.shopee_account_id: m for m in metrics}

    # 4. Audience Settings & Last Action
    settings = db.query(AudienceBudgetSetting).filter(AudienceBudgetSetting.shopee_account_id.in_(allowed_ids)).all()
    settings_map = {s.shopee_account_id: s for s in settings}

    # For status, we look at the LATEST action for each account
    # Using a subquery is safest or just query all today's actions?
    # Requirement: "remaining_before (dari log terakhir)". Log terakhir ever or today? 
    # Usually thresholds are about current state. Let's assume log from today or very recent.
    # But wait, budget is added when it runs low.
    # Let's simple fetch latest action for each account.
    latest_actions_sub = db.query(
        AudienceBudgetAction.shopee_account_id,
        func.max(AudienceBudgetAction.created_at).label("max_created")
    ).group_by(AudienceBudgetAction.shopee_account_id).subquery()

    latest_actions = db.query(AudienceBudgetAction).join(
        latest_actions_sub,
        (AudienceBudgetAction.shopee_account_id == latest_actions_sub.c.shopee_account_id) &
        (AudienceBudgetAction.created_at == latest_actions_sub.c.max_created)
    ).filter(AudienceBudgetAction.shopee_account_id.in_(allowed_ids)).all()
    
    action_map = {a.shopee_account_id: a for a in latest_actions}
    
    # 5 Added Budget Today
    added_today = db.query(
        AudienceBudgetAction.shopee_account_id,
        func.sum(AudienceBudgetAction.added_amount).label("total_added")
    ).filter(
        AudienceBudgetAction.date == date,
        AudienceBudgetAction.shopee_account_id.in_(allowed_ids)
    ).group_by(AudienceBudgetAction.shopee_account_id).all()
    added_map = {a.shopee_account_id: a.total_added for a in added_today}

    # Calculate Global Stats for Boros
    total_spend_all = sum(spend_map.values())
    total_gmv_all = sum(gmv_map.values())
    
    # Median ROAS calc
    roas_list = []
    for acc in accounts:
        s = spend_map.get(acc.id, 0)
        g = gmv_map.get(acc.id, 0)
        if s > 0:
            roas_list.append(g/s)
    
    roas_list.sort()
    n = len(roas_list)
    if n == 0:
        median_roas = 0
    elif n % 2 == 1:
        median_roas = roas_list[n//2]
    else:
        median_roas = (roas_list[n//2 - 1] + roas_list[n//2]) / 2

    # Build Response
    results = []
    for acc in accounts:
        # Data
        s_today = spend_map.get(acc.id, 0)
        g_today = gmv_map.get(acc.id, 0) or 0 # handle None from sum
        
        # Metrics
        metric_row = metrics_map.get(acc.id)
        roas_manual = metric_row.roas_manual if metric_row else None
        
        roas_auto = g_today / s_today if s_today > 0 else 0
        roas_final = roas_manual if roas_manual is not None else roas_auto

        # Boros Logic
        b_score, b_status, b_reason = calculate_boros_status(
            s_today, g_today, total_spend_all, total_gmv_all, median_roas
        )

        # Audience Logic
        setting = settings_map.get(acc.id)
        threshold = setting.min_remaining_threshold if setting else 3000
        gap = setting.min_gap_minutes if setting else 10
        
        last_action = action_map.get(acc.id)
        # Status calculation: "Jika remaining_before (dari log terakhir) <= threshold"
        # Wait, usually if we just added budget, remaining increases.
        # But if the trigger was 'threshold', it implies it was low.
        # Let's say: if last log exists, check its remaining_after. 
        # If remaining_after < threshold -> HAMPIR_HABIS (even after adding? unlikely but possible if added small amount)
        # OR if no log exists -> Check if we can know current balance? No API for that yet.
        # Let's rely on the prompt rule: "Jika remaining_before <= threshold"
        # But that logic applies to the MOMENT of trigger.
        # "Audience Status" should reflect CURRENT need.
        # If we just ADDED budget, we are probably AMAN.
        # If we haven't added for a long time?
        # Let's assume AMAN unless last action's remaining_after is still low.
        
        aud_status = "AMAN"
        if last_action:
             # If after adding, it's still low?
             if (last_action.remaining_after or 0) <= threshold:
                 aud_status = "HAMPIR_HABIS"
        
        last_add_str = last_action.created_at.strftime("%H:%M:%S") if last_action else None
        total_added = added_map.get(acc.id, 0) or 0

        results.append(AdsCenterAccountRow(
            account_id=acc.id,
            account_name=acc.account_name,
            spend_today=s_today,
            gmv_today=g_today,
            roas_auto=roas_auto if s_today > 0 else None,
            roas_manual=roas_manual,
            roas_final=roas_final,
            boros_score=b_score,
            boros_status=b_status,
            boros_reason=b_reason,
            audience_threshold=threshold,
            audience_gap_minutes=gap,
            audience_status=aud_status,
            last_add_budget_at=last_add_str,
            total_added_budget_today=total_added
        ))

    return results


@router.post("/spend/upsert", response_model=GenericSuccessResponse)
def upsert_spend(
    req: SpendUpsertRequest,
    current_user: User = Depends(require_role(["owner", "supervisor", "partner", "super_admin", "leader"])),
    db: Session = Depends(get_db)
):
    # Check scope
    allowed_ids = get_allowed_account_ids(db, current_user)
    if req.account_id not in allowed_ids:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Upsert logic based on Unique(date, account_id, spend_type)
    file_record = db.query(AdsDailySpend).filter(
        AdsDailySpend.date == req.date,
        AdsDailySpend.shopee_account_id == req.account_id,
        AdsDailySpend.spend_type == req.spend_type
    ).first()

    if file_record:
        file_record.spend_amount = req.spend_amount
        if req.note is not None:
            file_record.note = req.note
        file_record.created_by_user_id = current_user.id
        # file_record.created_at updated automatically? No, only on Creation.
        # Should we update timestamps? Model doesn't have updated_at.
    else:
        new_record = AdsDailySpend(
            date=req.date,
            shopee_account_id=req.account_id,
            spend_amount=req.spend_amount,
            spend_type=req.spend_type,
            note=req.note,
            created_by_user_id=current_user.id
        )
        db.add(new_record)
    
    db.commit()
    return GenericSuccessResponse(success=True, message="Spend updated", data=None)


@router.post("/metrics/upsert", response_model=GenericSuccessResponse)
def upsert_metrics(
    req: MetricsUpsertRequest,
    current_user: User = Depends(require_role(["owner", "supervisor", "partner", "super_admin"])),
    db: Session = Depends(get_db)
):
    # Leader excluded here as per prompt "Role: owner/supervisor/partner/super_admin only" in Step 5-(3)
    # Check scope
    allowed_ids = get_allowed_account_ids(db, current_user)
    if req.account_id not in allowed_ids:
        raise HTTPException(status_code=403, detail="Not allowed")

    record = db.query(AdsDailyMetrics).filter(
        AdsDailyMetrics.date == req.date,
        AdsDailyMetrics.shopee_account_id == req.account_id
    ).first()

    if record:
        if req.roas_manual is not None:
            record.roas_manual = req.roas_manual
        if req.revenue_manual is not None:
            record.revenue_manual = req.revenue_manual
        if req.note is not None:
            record.note = req.note
        record.created_by_user_id = current_user.id
    else:
        new_record = AdsDailyMetrics(
            date=req.date,
            shopee_account_id=req.account_id,
            roas_manual=req.roas_manual,
            revenue_manual=req.revenue_manual,
            note=req.note,
            created_by_user_id=current_user.id
        )
        db.add(new_record)
    
    db.commit()
    return GenericSuccessResponse(success=True, message="Metrics updated")


@router.get("/audience/settings")
def get_audience_settings(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed_ids = get_allowed_account_ids(db, current_user)
    if account_id not in allowed_ids:
        raise HTTPException(status_code=403, detail="Not allowed")

    setting = db.query(AudienceBudgetSetting).filter(AudienceBudgetSetting.shopee_account_id == account_id).first()
    if not setting:
        # Return default if not exists
        return {
            "shopee_account_id": account_id,
            "min_remaining_threshold": 3000,
            "min_gap_minutes": 10,
            "active_start_time": "05:00:00",
            "active_end_time": "00:00:00",
            "max_daily_add_budget": None,
            "is_enabled": True
        }
    return setting


@router.post("/audience/settings/upsert", response_model=GenericSuccessResponse)
def upsert_audience_settings(
    req: AudienceSettingsUpsertRequest,
    current_user: User = Depends(require_role(["owner", "supervisor", "partner", "super_admin"])),
    db: Session = Depends(get_db)
):
    allowed_ids = get_allowed_account_ids(db, current_user)
    if req.account_id not in allowed_ids:
        raise HTTPException(status_code=403, detail="Not allowed")
        
    setting = db.query(AudienceBudgetSetting).filter(AudienceBudgetSetting.shopee_account_id == req.account_id).first()
    if setting:
        setting.min_remaining_threshold = req.min_remaining_threshold
        setting.min_gap_minutes = req.min_gap_minutes
        setting.active_start_time = req.active_start_time
        setting.active_end_time = req.active_end_time
        setting.max_daily_add_budget = req.max_daily_add_budget
        setting.is_enabled = req.is_enabled
        setting.updated_by_user_id = current_user.id
    else:
        new_setting = AudienceBudgetSetting(
            shopee_account_id=req.account_id,
            min_remaining_threshold=req.min_remaining_threshold,
            min_gap_minutes=req.min_gap_minutes,
            active_start_time=req.active_start_time,
            active_end_time=req.active_end_time,
            max_daily_add_budget=req.max_daily_add_budget,
            is_enabled=req.is_enabled,
            updated_by_user_id=current_user.id
        )
        db.add(new_setting)
    
    db.commit()
    return GenericSuccessResponse(success=True, message="Settings updated")


@router.post("/audience/add-budget", response_model=GenericSuccessResponse)
def add_audience_budget(
    req: AudienceAddBudgetRequest,
    current_user: User = Depends(require_role(["owner", "supervisor", "partner", "super_admin", "leader"])),
    db: Session = Depends(get_db)
):
    # Host forbidden implicitly by require_role list (no 'host')
    
    allowed_ids = get_allowed_account_ids(db, current_user)
    if req.account_id not in allowed_ids:
        raise HTTPException(status_code=403, detail="Not allowed")

    if req.added_amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    # Get settings for gap check
    setting = db.query(AudienceBudgetSetting).filter(AudienceBudgetSetting.shopee_account_id == req.account_id).first()
    gap_minutes = setting.min_gap_minutes if setting else 10

    # Check last action
    last_action = db.query(AudienceBudgetAction).filter(
        AudienceBudgetAction.shopee_account_id == req.account_id
    ).order_by(desc(AudienceBudgetAction.created_at)).first()

    if last_action:
        delta = datetime.now() - last_action.created_at
        if delta.total_seconds() < gap_minutes * 60:
            raise HTTPException(
                status_code=409, 
                detail="Tunggu dulu ya, jeda tambah modal belum lewat ⏳"
            )

    # Insert log
    new_action = AudienceBudgetAction(
        date=req.date,
        time=datetime.now().strftime("%H:%M:%S"),
        shopee_account_id=req.account_id,
        remaining_before=req.remaining_before,
        added_amount=req.added_amount,
        remaining_after=(req.remaining_before or 0) + req.added_amount,
        trigger_reason="manual", # endpoint called by manual action usually
        created_by_user_id=current_user.id
    )
    db.add(new_action)
    db.commit()

    return GenericSuccessResponse(success=True, message="Budget added successfully")


@router.get("/logs/spend", response_model=List[LogsSpendRow])
def get_spend_logs(
    from_date: date,
    to_date: date,
    account_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed_ids = get_allowed_account_ids(db, current_user)
    if not allowed_ids: return []

    query = db.query(AdsDailySpend).filter(
        AdsDailySpend.date >= from_date, 
        AdsDailySpend.date <= to_date,
        AdsDailySpend.shopee_account_id.in_(allowed_ids)
    )
    if account_id:
        if account_id not in allowed_ids: raise HTTPException(status_code=403, detail="Denied")
        query = query.filter(AdsDailySpend.shopee_account_id == account_id)
        
    logs = query.order_by(desc(AdsDailySpend.date)).all()
    
    return [LogsSpendRow(
        id=l.id, date=l.date, account_name=l.account.account_name,
        spend_amount=l.spend_amount, spend_type=l.spend_type, note=l.note,
        created_by=l.creator.username if l.creator else None, created_at=l.created_at
    ) for l in logs]


@router.get("/logs/audience", response_model=List[LogsAudienceRow])
def get_audience_logs(
    from_date: date,
    to_date: date,
    account_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed_ids = get_allowed_account_ids(db, current_user)
    if not allowed_ids: return []

    query = db.query(AudienceBudgetAction).filter(
        AudienceBudgetAction.date >= from_date, 
        AudienceBudgetAction.date <= to_date,
        AudienceBudgetAction.shopee_account_id.in_(allowed_ids)
    )
    if account_id:
        if account_id not in allowed_ids: raise HTTPException(status_code=403, detail="Denied")
        query = query.filter(AudienceBudgetAction.shopee_account_id == account_id)
        
    logs = query.order_by(desc(AudienceBudgetAction.created_at)).all()
    
    return [LogsAudienceRow(
        id=l.id, date=l.date, time=l.time, account_name=l.account.account_name,
        remaining_before=l.remaining_before, added_amount=l.added_amount,
        remaining_after=l.remaining_after, trigger_reason=l.trigger_reason,
        created_by=l.creator.username if l.creator else None, created_at=l.created_at
    ) for l in logs]

   
@router.get("/logs/roas", response_model=List[LogsRoasRow])
def get_roas_logs(
    from_date: date,
    to_date: date,
    account_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed_ids = get_allowed_account_ids(db, current_user)
    if not allowed_ids: return []

    query = db.query(AdsDailyMetrics).filter(
        AdsDailyMetrics.date >= from_date, 
        AdsDailyMetrics.date <= to_date,
        AdsDailyMetrics.shopee_account_id.in_(allowed_ids)
    )
    if account_id:
        if account_id not in allowed_ids: raise HTTPException(status_code=403, detail="Denied")
        query = query.filter(AdsDailyMetrics.shopee_account_id == account_id)
        
    logs = query.order_by(desc(AdsDailyMetrics.date)).all()
    
    return [LogsRoasRow(
        id=l.id, date=l.date, account_name=l.account.account_name,
        roas_manual=l.roas_manual or 0.0, revenue_manual=l.revenue_manual,
        note=l.note, created_by=l.creator.username if l.creator else None, 
        created_at=l.created_at
    ) for l in logs]
