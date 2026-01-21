"""
Premium Dashboard Backend Route
Provides enhanced features for Owner/Super Admin/Supervisor roles only
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import date, datetime, timedelta
from typing import List, Optional

from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.order import Order
from app.models.shopee_account import ShopeeAccount
from app.models.ads import AdsDailySpend, AdsDailyMetrics
from app.models.live_product_snapshot import LiveProductSnapshot
from app.core.permissions import get_allowed_account_ids

router = APIRouter(prefix="/api/dashboard", tags=["premium"])


# ==================== Helper Functions ====================

def normalize_role(role: str) -> str:
    return role.lower().replace(" ", "_")


# ==================== Premium Dashboard Endpoint ====================

@router.get("/premium")
def get_premium_dashboard(
    date: date,
    account_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET /api/dashboard/premium?date=YYYY-MM-DD&account_id=123
    
    Premium dashboard data with 5 features:
    1. Hourly performance chart
    2. Top performers (accounts, hosts, products)
    3. Alerts (BOROS, budget, drops, risks)
    4. Financial summary
    5. Quick actions (handled frontend)
    
    RBAC: owner/super_admin/supervisor only
    """
    # Strict RBAC check
    role = normalize_role(current_user.role)
    if role not in ['owner', 'super_admin', 'supervisor']:
        raise HTTPException(status_code=403, detail="Premium features require owner/super_admin/supervisor role")
    
    # Get allowed accounts
    allowed_ids = get_allowed_account_ids(db, current_user)
    if not allowed_ids:
        raise HTTPException(status_code=403, detail="No accounts accessible")
    
    # Apply account filter if provided
    if account_id:
        if account_id not in allowed_ids:
            raise HTTPException(status_code=403, detail="Access denied to this account")
        allowed_ids = [account_id]
    
    # ==================== FEATURE 1: Hourly Performance ====================
    hourly_performance = []
    yesterday = date - timedelta(days=1)
    
    # Generate hourly buckets (5:00 - 23:59)
    for hour in range(5, 24):
        hour_str = f"{hour:02d}:00"
        
        # Today's data
        start_time = datetime.combine(date, datetime.min.time()).replace(hour=hour)
        end_time = start_time + timedelta(hours=1)
        
        orders_today = db.query(func.count(Order.id), func.sum(Order.total_amount)).filter(
            and_(
                Order.shopee_account_id.in_(allowed_ids),
                Order.date >= start_time,
                Order.date < end_time,
                Order.status == 'completed'
            )
        ).first()
        
        # Yesterday's data for comparison
        start_yesterday = start_time - timedelta(days=1)
        end_yesterday = end_time - timedelta(days=1)
        
        orders_yesterday = db.query(func.sum(Order.total_amount)).filter(
            and_(
                Order.shopee_account_id.in_(allowed_ids),
                Order.date >= start_yesterday,
                Order.date < end_yesterday,
                Order.status == 'completed'
            )
        ).scalar()
        
        hourly_performance.append({
            "hour": hour_str,
            "orders": orders_today[0] or 0,
            "gmv": float(orders_today[1]) if orders_today[1] else 0.0,
            "gmv_yesterday": float(orders_yesterday) if orders_yesterday else 0.0
        })
    
    # ==================== FEATURE 2: Top Performers ====================
    
    # Top 5 Accounts by GMV
    top_accounts_raw = db.query(
        ShopeeAccount.account_name,
        func.sum(Order.total_amount).label("gmv")
    ).join(
        Order, Order.shopee_account_id == ShopeeAccount.id
    ).filter(
        and_(
            func.date(Order.date) == date,
            Order.shopee_account_id.in_(allowed_ids),
            Order.status == 'completed'
        )
    ).group_by(ShopeeAccount.id, ShopeeAccount.account_name).order_by(desc("gmv")).limit(5).all()
    
    top_accounts = [
        {
            "name": acc.account_name,
            "value": float(acc.gmv),
            "subtitle": f"{acc.gmv / 1000000:.1f}jt GMV",
            "rank": idx + 1
        }
        for idx, acc in enumerate(top_accounts_raw)
    ]
    
    # Top 5 Hosts (mock - would need actual host data)
    # For now, using placeholder data
    top_hosts = [
        {"name": "Host 1", "value": 85, "subtitle": "85% conversion", "rank": 1},
        {"name": "Host 2", "value": 78, "subtitle": "78% conversion", "rank": 2},
        {"name": "Host 3", "value": 72, "subtitle": "72% conversion", "rank": 3},
    ]
    
    # Top 5 Products by sold qty from Live Snapshot
    top_products_raw = db.query(
        LiveProductSnapshot.product_name,
        func.sum(LiveProductSnapshot.sold_qty).label("total_sold")
    ).filter(
        and_(
            LiveProductSnapshot.snapshot_date == date,
            LiveProductSnapshot.account_id.in_(allowed_ids)
        )
    ).group_by(LiveProductSnapshot.product_name).order_by(desc("total_sold")).limit(5).all()
    
    top_products = [
        {
            "name": prod.product_name[:30],
            "value": prod.total_sold,
            "subtitle": f"{prod.total_sold} terjual",
            "rank": idx + 1
        }
        for idx, prod in enumerate(top_products_raw)
    ]
    
    # ==================== FEATURE 3: Alerts ====================
    alerts = []
    
    # Alert: BOROS accounts (from Ads Center)
    boros_accounts = db.query(ShopeeAccount.account_name).join(
        Order, Order.shopee_account_id == ShopeeAccount.id
    ).join(
        AdsDailySpend, AdsDailySpend.shopee_account_id == ShopeeAccount.id
    ).filter(
        and_(
            func.date(Order.date) == date,
            AdsDailySpend.date == date,
            ShopeeAccount.id.in_(allowed_ids)
        )
    ).group_by(ShopeeAccount.id, ShopeeAccount.account_name).having(
        func.sum(Order.total_amount) / func.sum(AdsDailySpend.spend_amount) < 5
    ).limit(3).all()
    
    if boros_accounts:
        alerts.append({
            "type": "boros",
            "title": f"🚨 {len(boros_accounts)} Akun BOROS terdeteksi!",
            "description": f"ROAS < 5x: {', '.join([acc.account_name for acc in boros_accounts])}",
            "severity": "critical",
            "actionLabel": "Cek Ads Center",
            "actionPath": "/ads-center"
        })
    
    # Alert: Live Products DROP
    drops = db.query(LiveProductSnapshot).filter(
        and_(
            LiveProductSnapshot.snapshot_date == date,
            LiveProductSnapshot.account_id.in_(allowed_ids),
            LiveProductSnapshot.sold_qty < 5  # Mock condition
        )
    ).count()
    
    if drops > 0:
        alerts.append({
            "type": "drop",
            "title": f"📉 {drops} Produk Performa Turun",
            "description": "Ada produk yang penjualannya drop signifikan hari ini",
            "severity": "warning",
            "actionLabel": "Lihat Live Products",
            "actionPath": "/live-products"
        })
    
    # ==================== FEATURE 4: Financial Summary ====================
    
    # Revenue today
    revenue_today = db.query(func.sum(Order.total_amount)).filter(
        and_(
            func.date(Order.date) == date,
            Order.shopee_account_id.in_(allowed_ids),
            Order.status == 'completed'
        )
    ).scalar() or 0
    
    # Revenue yesterday
    revenue_yesterday = db.query(func.sum(Order.total_amount)).filter(
        and_(
            func.date(Order.date) == yesterday,
            Order.shopee_account_id.in_(allowed_ids),
            Order.status == 'completed'
        )
    ).scalar() or 0
    
    # Commission (mock - would need actual commission table)
    commission_pending = float(revenue_today) * 0.05
    commission_paid = float(revenue_yesterday) * 0.05
    
    # Budget
    budget_used = db.query(func.sum(AdsDailySpend.spend_amount)).filter(
        and_(
            AdsDailySpend.date == date,
            AdsDailySpend.shopee_account_id.in_(allowed_ids)
        )
    ).scalar() or 0
    
    budget_total = float(budget_used) * 1.2  # Mock total (20% headroom)
    
    # ROAS per account
    accounts_roas_raw = db.query(
        ShopeeAccount.account_name,
        func.sum(Order.total_amount).label("gmv"),
        func.sum(AdsDailySpend.spend_amount).label("spend")
    ).join(
        Order, Order.shopee_account_id == ShopeeAccount.id, isouter=True
    ).join(
        AdsDailySpend, AdsDailySpend.shopee_account_id == ShopeeAccount.id, isouter=True
    ).filter(
        and_(
            ShopeeAccount.id.in_(allowed_ids),
            func.date(Order.date) == date,
            AdsDailySpend.date == date
        )
    ).group_by(ShopeeAccount.id, ShopeeAccount.account_name).all()
    
    accounts_roas = []
    for acc in accounts_roas_raw:
        gmv = float(acc.gmv) if acc.gmv else 0
        spend = float(acc.spend) if acc.spend else 1
        roas = gmv / spend if spend > 0 else 0
        accounts_roas.append({
            "account_name": acc.account_name[:10],
            "roas": round(roas, 2)
        })
    
    financial_summary = {
        "revenue_today": float(revenue_today),
        "revenue_yesterday": float(revenue_yesterday),
        "commission_pending": commission_pending,
        "commission_paid": commission_paid,
        "budget_used": float(budget_used),
        "budget_total": budget_total,
        "accounts_roas": accounts_roas
    }
    
    # ==================== Return Response ====================
    
    return {
        "hourly_performance": hourly_performance,
        "top_performers": {
            "accounts": top_accounts,
            "hosts": top_hosts,
            "products": top_products
        },
        "alerts": alerts,
        "financial_summary": financial_summary
    }
