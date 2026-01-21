"""
Dashboard Owner Mode - Premium Analytics Endpoint
Provides comprehensive business insights for owner role
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
import logging

from app.database import get_db
from app.models.order import Order
from app.models.ads import AdsDailySpend, AdsDailyMetrics
from app.models.shopee_account import ShopeeAccount
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/owner")
async def get_owner_dashboard(
    date_param: Optional[str] = Query(None, alias="date"),
    account_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Owner Dashboard - Premium Analytics
    Returns comprehensive business insights for owner monitoring
    """
    try:
        # Parse date
        target_date = date.fromisoformat(date_param) if date_param else date.today()
        yesterday = target_date - timedelta(days=1)
        
        logger.info(f"Owner dashboard requested for date: {target_date}, account_id: {account_id}")
        
        # Base query filters
        account_filter = [ShopeeAccount.id == account_id] if account_id else []
        
        # ===== KPI CALCULATIONS =====
        
        # GMV Today (from orders)
        gmv_query = db.query(func.sum(Order.total_amount)).filter(
            func.date(Order.date) == target_date,
            *account_filter
        )
        if account_id:
            gmv_query = gmv_query.filter(Order.shopee_account_id == account_id)
        gmv_today = float(gmv_query.scalar() or 0)
        
        # Orders Today
        orders_query = db.query(func.count(Order.id)).filter(
            func.date(Order.date) == target_date
        )
        if account_id:
            orders_query = orders_query.filter(Order.shopee_account_id == account_id)
        orders_today = orders_query.scalar() or 0
        
        # Commission Net
        commission_query = db.query(func.sum(Order.commission_amount)).filter(
            func.date(Order.date) == target_date
        )
        if account_id:
            commission_query = commission_query.filter(Order.shopee_account_id == account_id)
        commission_net = float(commission_query.scalar() or 0)
        
        # Ads Spend Total
        spend_query = db.query(func.sum(AdsDailySpend.spend_amount)).filter(
            AdsDailySpend.date == target_date
        )
        if account_id:
            spend_query = spend_query.filter(AdsDailySpend.shopee_account_id == account_id)
        ads_spend_total = float(spend_query.scalar() or 0)
        
        # ROAS Today
        roas_today = (gmv_today / ads_spend_total) if ads_spend_total > 0 else 0
        
        # Profit Estimate (GMV - Spend)
        profit_estimate = gmv_today - ads_spend_total
        
        # Bonus Host Today (placeholder - would need bonus calculation logic)
        bonus_host_today = 0  # TODO: Implement bonus calculation
        
        # Audience Balance (from latest audience budget action)
        audience_balance = None  # TODO: Query latest audience balance if available
        
        # ===== WAR ROOM DATA =====
        
        # Account Ranking
        account_ranking = []
        accounts = db.query(ShopeeAccount).filter(ShopeeAccount.is_active == True).all()
        
        for acc in accounts:
            if account_id and acc.id != account_id:
                continue
                
            acc_gmv = db.query(func.sum(Order.total_amount)).filter(
                func.date(Order.date) == target_date,
                Order.shopee_account_id == acc.id
            ).scalar() or 0
            
            acc_orders = db.query(func.count(Order.id)).filter(
                func.date(Order.date) == target_date,
                Order.shopee_account_id == acc.id
            ).scalar() or 0
            
            acc_commission = db.query(func.sum(Order.commission_amount)).filter(
                func.date(Order.date) == target_date,
                Order.shopee_account_id == acc.id
            ).scalar() or 0
            
            acc_spend = db.query(func.sum(AdsDailySpend.spend_amount)).filter(
                AdsDailySpend.date == target_date,
                AdsDailySpend.shopee_account_id == acc.id
            ).scalar() or 0
            
            acc_roas = (acc_gmv / acc_spend) if acc_spend > 0 else 0
            
            # Determine status based on ROAS
            if acc_roas >= 8:
                status = "AMAN"
            elif acc_roas >= 5:
                status = "WASPADA"
            else:
                status = "BOROS"
            
            account_ranking.append({
                "account_id": acc.id,
                "account_name": acc.account_name,
                "gmv": float(acc_gmv),
                "orders": acc_orders,
                "commission": float(acc_commission),
                "spend": float(acc_spend),
                "roas": round(acc_roas, 2),
                "status": status
            })
        
        # Sort by GMV descending
        account_ranking.sort(key=lambda x: x["gmv"], reverse=True)
        
        # Orders per Hour (05:00 - 00:00)
        orders_per_hour = []
        for hour in range(5, 24):  # 05:00 to 23:00
            hour_str = f"{hour:02d}:00"
            # Count orders in this hour
            hour_orders = db.query(func.count(Order.id)).filter(
                func.date(Order.date) == target_date,
                func.extract('hour', Order.date) == hour
            )
            if account_id:
                hour_orders = hour_orders.filter(Order.shopee_account_id == account_id)
            
            count = hour_orders.scalar() or 0
            orders_per_hour.append({
                "hour": hour_str,
                "orders": count
            })
        
        # Shift Scoreboard (4 shifts)
        shifts = [
            {"name": "Pagi (05:00-11:00)", "start": 5, "end": 11},
            {"name": "Siang (11:00-17:00)", "start": 11, "end": 17},
            {"name": "Sore (17:00-21:00)", "start": 17, "end": 21},
            {"name": "Malam (21:00-00:00)", "start": 21, "end": 24}
        ]
        
        shift_scoreboard = []
        for shift in shifts:
            shift_gmv = db.query(func.sum(Order.total_amount)).filter(
                func.date(Order.date) == target_date,
                func.extract('hour', Order.date) >= shift["start"],
                func.extract('hour', Order.date) < shift["end"]
            )
            if account_id:
                shift_gmv = shift_gmv.filter(Order.shopee_account_id == account_id)
            
            shift_orders = db.query(func.count(Order.id)).filter(
                func.date(Order.date) == target_date,
                func.extract('hour', Order.date) >= shift["start"],
                func.extract('hour', Order.date) < shift["end"]
            )
            if account_id:
                shift_orders = shift_orders.filter(Order.shopee_account_id == account_id)
            
            total_gmv = shift_gmv.scalar() or 0
            total_orders = shift_orders.scalar() or 0
            
            # MVP Host (placeholder - would need employee assignment tracking)
            mvp_host = "Data belum tersedia"
            mvp_gmv = 0
            
            shift_scoreboard.append({
                "shift_name": shift["name"],
                "total_gmv": float(total_gmv),
                "total_orders": total_orders,
                "mvp_host": mvp_host,
                "mvp_gmv": float(mvp_gmv)
            })
        
        # ===== HARDCORE INSIGHTS =====
        
        # Product Drops (compare today vs yesterday)
        # Note: Requires product_name in orders table
        product_drops = []
        products_today = db.query(
            Order.product_name,
            func.count(Order.id).label('count')
        ).filter(
            func.date(Order.date) == target_date,
            Order.product_name.isnot(None)
        ).group_by(Order.product_name).all()
        
        for product in products_today[:10]:  # Top 10 products
            yesterday_count = db.query(func.count(Order.id)).filter(
                func.date(Order.date) == yesterday,
                Order.product_name == product.product_name
            ).scalar() or 0
            
            if yesterday_count > 0:
                drop_percent = ((product.count - yesterday_count) / yesterday_count) * 100
                if drop_percent < -30:  # Significant drop
                    product_drops.append({
                        "product_name": product.product_name,
                        "yesterday_orders": yesterday_count,
                        "today_orders": product.count,
                        "drop_percent": round(drop_percent, 1)
                    })
        
        # Profit Hunters (Top 5 products by commission)
        profit_hunters = db.query(
            Order.product_name,
            func.sum(Order.commission_amount).label('total_commission'),
            func.count(Order.id).label('orders')
        ).filter(
            func.date(Order.date) == target_date,
            Order.product_name.isnot(None)
        ).group_by(Order.product_name).order_by(
            desc('total_commission')
        ).limit(5).all()
        
        profit_hunters_list = [
            {
                "product_name": p.product_name,
                "total_commission": float(p.total_commission),
                "orders": p.orders
            }
            for p in profit_hunters
        ]
        
        # Risk Detector (account dependency)
        if len(account_ranking) > 0:
            top_account = account_ranking[0]
            top_account_dependency = (top_account["gmv"] / gmv_today * 100) if gmv_today > 0 else 0
            risk_detector = {
                "top_account_dependency": round(top_account_dependency, 1),
                "account_name": top_account["account_name"],
                "is_risky": top_account_dependency > 60
            }
        else:
            risk_detector = {
                "top_account_dependency": 0,
                "account_name": "N/A",
                "is_risky": False
            }
        
        # Boros Detector (accounts with ROAS < threshold)
        boros_threshold = 5.0  # Dynamic threshold (could be configurable)
        boros_accounts = [acc["account_name"] for acc in account_ranking if acc["roas"] < boros_threshold and acc["spend"] > 0]
        
        boros_detector = {
            "threshold": boros_threshold,
            "boros_accounts": boros_accounts
        }
        
        # Weak Shifts (shifts below target)
        weak_shifts = []
        target_gmv_per_shift = gmv_today / 4 if gmv_today > 0 else 0  # Equal distribution
        
        for shift in shift_scoreboard:
            if target_gmv_per_shift > 0:
                gap_percent = ((shift["total_gmv"] - target_gmv_per_shift) / target_gmv_per_shift) * 100
                if gap_percent < -30:  # 30% below target
                    recommendation = "Tambah host atau boost iklan" if gap_percent < -50 else "Monitor performa"
                    weak_shifts.append({
                        "shift_name": shift["shift_name"],
                        "gmv": shift["total_gmv"],
                        "target": target_gmv_per_shift,
                        "gap_percent": round(gap_percent, 1),
                        "recommendation": recommendation
                    })
        
        # ===== OWNER ALERTS =====
        alerts = []
        
        # Alert: High account dependency
        if risk_detector["is_risky"]:
            alerts.append({
                "level": "critical",
                "message": f"⚠️ Akun {risk_detector['account_name']} dominasi {risk_detector['top_account_dependency']}% GMV! Diversifikasi ASAP!",
                "action": "Aktifkan akun cadangan"
            })
        
        # Alert: Boros accounts
        if len(boros_accounts) > 0:
            alerts.append({
                "level": "warning",
                "message": f"💸 {len(boros_accounts)} akun boros terdeteksi (ROAS < {boros_threshold}x): {', '.join(boros_accounts[:3])}",
                "action": "Review strategi iklan"
            })
        
        # Alert: Weak shifts
        if len(weak_shifts) > 0:
            alerts.append({
                "level": "warning",
                "message": f"📉 {len(weak_shifts)} shift lemah hari ini: {', '.join([s['shift_name'] for s in weak_shifts])}",
                "action": "Tambah host atau boost iklan"
            })
        
        # Alert: Low ROAS overall
        if roas_today < 5.0 and ads_spend_total > 0:
            alerts.append({
                "level": "critical",
                "message": f"🚨 ROAS hari ini cuma {roas_today:.2f}x! Target minimal 5x!",
                "action": "Stop iklan yang tidak efektif"
            })
        
        # ===== SYNC STATUS =====
        # Placeholder - would need actual sync tracking
        sync_status = {
            "status": "LIVE",  # LIVE | DELAY | PUTUS
            "last_update": datetime.now().isoformat(),
            "delay_minutes": 0
        }
        
        # ===== RESPONSE =====
        return {
            "sync_status": sync_status,
            "kpi": {
                "gmv_today": float(gmv_today),
                "orders_today": orders_today,
                "commission_net": float(commission_net),
                "ads_spend_total": float(ads_spend_total),
                "roas_today": round(roas_today, 2),
                "profit_estimate": float(profit_estimate),
                "bonus_host_today": float(bonus_host_today),
                "audience_balance": audience_balance
            },
            "war_room": {
                "account_ranking": account_ranking,
                "orders_per_hour": orders_per_hour,
                "shift_scoreboard": shift_scoreboard
            },
            "insights": {
                "product_drops": product_drops,
                "profit_hunters": profit_hunters_list,
                "risk_detector": risk_detector,
                "boros_detector": boros_detector,
                "weak_shifts": weak_shifts
            },
            "alerts": alerts
        }
    
    except Exception as e:
        logger.error(f"Owner dashboard error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to load owner dashboard: {str(e)}")
