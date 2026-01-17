"""
Daily Insights & Summary Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc, and_
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, date, time
from pydantic import BaseModel

from app.database import get_db
from app.models.order import Order
from app.models.shopee_account import ShopeeAccount
from app.models.user import User
from app.models.shift_template import ShiftTemplate
from app.auth.dependencies import require_role

router = APIRouter()

# --- Schemas ---

class KPISummary(BaseModel):
    total_orders: int
    total_gmv: float
    total_commission: float
    total_bonus: float

class TopEntity(BaseModel):
    id: Optional[Any] = None
    name: str = "Unknown"
    orders: int = 0
    gmv: float = 0.0
    commission: float = 0.0
    bonus: float = 0.0

class DailySummaryResponse(BaseModel):
    date: str
    scope: str
    kpi: KPISummary
    best_account_today: TopEntity
    best_host_today: Optional[TopEntity]
    best_shift_today: TopEntity
    weak_shift_today: TopEntity
    notes: List[str]

class ProductWarning(BaseModel):
    product_id: str
    product_name: str
    orders_today: int
    orders_yesterday: int
    drop_percent: float
    account_name: str

class ProductProfit(BaseModel):
    product_id: str
    product_name: str
    total_commission: float
    total_orders: int
    commission_per_order: float
    account_name: str

class ShiftSummary(BaseModel):
    shift_name: str
    orders: int
    gmv: float
    commission: float

class HostRankingResponse(BaseModel):
    top: List[TopEntity]
    needs_attention: List[TopEntity]

class DailyInsightsResponse(BaseModel):
    date: str
    warnings: Dict[str, List[ProductWarning]]
    top_profit_products: List[ProductProfit]
    strongest_accounts: List[TopEntity]
    host_ranking: HostRankingResponse
    shift_summary: List[ShiftSummary]
    dependency_risk: List[Dict[str, str]]
    action_items: List[str]

# --- Helpers ---

def get_shift_name(dt: datetime) -> str:
    # Logic matching Seed Data: Shift 1 (05-10), Shift 2 (10-15), Shift 3 (15-20), Shift 4 (20-00)
    # Using naive hour extraction
    h = dt.hour
    if 5 <= h < 10: return "Shift 1 (Pagi)"
    if 10 <= h < 15: return "Shift 2 (Siang)"
    if 15 <= h < 20: return "Shift 3 (Sore)"
    if 20 <= h < 24: return "Shift 4 (Malam)"
    return "Outside Shift"

# --- Endpoints ---

@router.get("/daily-summary", response_model=DailySummaryResponse)
async def get_daily_summary(
    date_str: str = Query(..., alias="date"),
    shop_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner")) # Owner only
):
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(400, "Invalid date format YYYY-MM-DD")

    # Base Query
    base_query = db.query(Order).filter(func.date(Order.date) == target_date)
    if shop_id:
        base_query = base_query.filter(Order.shopee_account_id == shop_id)
        
    orders = base_query.all()
    
    # KPI Calculation
    total_orders = len(orders)
    total_gmv = sum(float(o.total_amount) for o in orders)
    total_commission = sum(float(o.commission_amount) for o in orders)
    total_bonus = 0 # Placeholder: Integrate calculation if needed, for now simplistic
    
    # Aggregations via Python (Simpler for complex logic validation, can be SQL optimized later)
    # Best Account
    acc_stats = {}
    host_stats = {}
    shift_stats = {
        "Shift 1 (Pagi)": {"orders": 0, "gmv": 0},
        "Shift 2 (Siang)": {"orders": 0, "gmv": 0},
        "Shift 3 (Sore)": {"orders": 0, "gmv": 0},
        "Shift 4 (Malam)": {"orders": 0, "gmv": 0},
        "Outside Shift": {"orders": 0, "gmv": 0} 
    }
    
    for o in orders:
        # Account
        if o.shopee_account_id not in acc_stats:
            acc_name = o.shopee_account.account_name if o.shopee_account else "Unknown"
            acc_stats[o.shopee_account_id] = {"name": acc_name, "orders": 0, "gmv": 0, "commission": 0}
        acc_stats[o.shopee_account_id]["orders"] += 1
        acc_stats[o.shopee_account_id]["gmv"] += float(o.total_amount)
        acc_stats[o.shopee_account_id]["commission"] += float(o.commission_amount)
        
        # Host (if handler_user_id exists)
        h_id = o.handler_user_id or 0
        if h_id not in host_stats:
            h_name = o.handler.username if o.handler else "Unknown" if h_id == 0 else "System"
            host_stats[h_id] = {"name": h_name, "orders": 0, "gmv": 0}
        host_stats[h_id]["orders"] += 1
        host_stats[h_id]["gmv"] += float(o.total_amount)
        
        # Shift
        s_name = get_shift_name(o.date)
        shift_stats[s_name]["orders"] += 1
        shift_stats[s_name]["gmv"] += float(o.total_amount)

    # Determine Best/Weak
    best_acc = max(acc_stats.values(), key=lambda x: x['orders']) if acc_stats else {"name": "-", "orders": 0, "gmv": 0, "commission": 0}
    best_host = max(host_stats.values(), key=lambda x: x['orders']) if host_stats else None
    
    valid_shifts = {k:v for k,v in shift_stats.items() if k != "Outside Shift"}
    best_shift = max(valid_shifts.items(), key=lambda x: x[1]['orders'])
    weak_shift = min(valid_shifts.items(), key=lambda x: x[1]['orders'])
    
    # Generate Notes
    notes = []
    if total_orders > 0 and weak_shift[1]['orders'] < (total_orders * 0.1): 
         notes.append(f"{weak_shift[0]} perlu perhatian khusus ⚠️")
    if total_commission > 1000000:
         notes.append("Komisi hari ini tembus 1 Juta! 🔥")
         
    return DailySummaryResponse(
        date=date_str,
        scope="single_account" if shop_id else "all_accounts",
        kpi=KPISummary(
            total_orders=total_orders,
            total_gmv=total_gmv,
            total_commission=total_commission,
            total_bonus=total_bonus
        ),
        best_account_today=TopEntity(name=best_acc['name'], orders=best_acc['orders'], gmv=best_acc['gmv'], commission=best_acc.get('commission',0)),
        best_host_today=TopEntity(name=best_host['name'], orders=best_host['orders'], gmv=best_host['gmv']) if best_host else None,
        best_shift_today=TopEntity(name=best_shift[0], orders=best_shift[1]['orders']),
        weak_shift_today=TopEntity(name=weak_shift[0], orders=weak_shift[1]['orders']),
        notes=notes
    )

@router.get("/daily", response_model=DailyInsightsResponse)
async def get_daily_insights(
    date_str: str = Query(..., alias="date"),
    shop_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("leader")) # Leader+
):
    try:
        today = datetime.strptime(date_str, "%Y-%m-%d").date()
        yesterday = today - timedelta(days=1)
    except ValueError:
        raise HTTPException(400, "Invalid date format")

    # 1. Product Drops (Comparison)
    # Get today's product stats
    q_today = db.query(
        Order.product_id, Order.product_name, Order.shopee_account_id, 
        func.count(Order.id).label('orders')
    ).filter(
        func.date(Order.date) == today,
        Order.product_id.isnot(None)
    )
    if shop_id: q_today = q_today.filter(Order.shopee_account_id == shop_id)
    stats_today = q_today.group_by(Order.product_id, Order.shopee_account_id).all()
    
    # Get yesterday's product stats
    q_yester = db.query(
        Order.product_id, func.count(Order.id).label('orders')
    ).filter(
        func.date(Order.date) == yesterday,
        Order.product_id.isnot(None)
    )
    if shop_id: q_yester = q_yester.filter(Order.shopee_account_id == shop_id)
    stats_yester = {r.product_id: r.orders for r in q_yester.group_by(Order.product_id).all()}
    
    warnings = []
    # Identify drops
    for p in stats_today:
        y_orders = stats_yester.get(p.product_id, 0)
        t_orders = p.orders
        if y_orders > 10: # Only check if volume is significant
            drop = (y_orders - t_orders) / y_orders
            if drop >= 0.4: # 40% drop
                acc = db.query(ShopeeAccount).get(p.shopee_account_id)
                warnings.append(ProductWarning(
                    product_id=p.product_id,
                    product_name=p.product_name or "Unknown Product",
                    orders_today=t_orders,
                    orders_yesterday=y_orders,
                    drop_percent=round(drop * 100, 1),
                    account_name=acc.account_name if acc else "-"
                ))
    
    # 2. Top Profit Products
    q_profit = db.query(
        Order.product_id, Order.product_name, Order.shopee_account_id,
        func.sum(Order.commission_amount).label('total_comm'),
        func.count(Order.id).label('orders')
    ).filter(func.date(Order.date) == today, Order.product_id.isnot(None))
    if shop_id: q_profit = q_profit.filter(Order.shopee_account_id == shop_id)
    
    profit_rows = q_profit.group_by(Order.product_id, Order.shopee_account_id).order_by(desc('total_comm')).limit(5).all()
    
    top_products = []
    for r in profit_rows:
        acc = db.query(ShopeeAccount).get(r.shopee_account_id)
        top_products.append(ProductProfit(
            product_id=r.product_id,
            product_name=r.product_name or "Unknown",
            total_commission=float(r.total_comm),
            total_orders=r.orders,
            commission_per_order=float(r.total_comm) / r.orders if r.orders > 0 else 0,
            account_name=acc.account_name if acc else "-"
        ))
        
    # 3. Strongest Accounts
    q_acc = db.query(
        Order.shopee_account_id, 
        func.count(Order.id).label('orders'),
        func.sum(Order.total_amount).label('gmv'),
        func.sum(Order.commission_amount).label('comm')
    ).filter(func.date(Order.date) == today)
    if shop_id: q_acc = q_acc.filter(Order.shopee_account_id == shop_id)
    
    acc_rows = q_acc.group_by(Order.shopee_account_id).order_by(desc('gmv')).limit(3).all()
    strongest_accounts = []
    total_gmv_day = 0
    
    for r in acc_rows:
        acc = db.query(ShopeeAccount).get(r.shopee_account_id)
        strongest_accounts.append(TopEntity(
            id=r.shopee_account_id,
            name=acc.account_name if acc else "-",
            orders=r.orders,
            gmv=float(r.gmv),
            commission=float(r.comm)
        ))
        total_gmv_day += float(r.gmv)

    # 4. Host Ranking (Mock logic for now as we might have missing handler_id)
    # Using existing data logic
    host_ranking = HostRankingResponse(top=[], needs_attention=[])
    
    # 5. Shift Summary
    # Re-use logic from summary but structured list
    shift_aggregated = {
        "Shift 1 (Pagi)": {"orders": 0, "gmv": 0, "comm": 0},
        "Shift 2 (Siang)": {"orders": 0, "gmv": 0, "comm": 0},
        "Shift 3 (Sore)": {"orders": 0, "gmv": 0, "comm": 0},
        "Shift 4 (Malam)": {"orders": 0, "gmv": 0, "comm": 0}
    }
    
    all_orders = db.query(Order).filter(func.date(Order.date) == today)
    if shop_id: all_orders = all_orders.filter(Order.shopee_account_id == shop_id)
    
    for o in all_orders:
        sn = get_shift_name(o.date)
        if sn in shift_aggregated:
            shift_aggregated[sn]['orders'] += 1
            shift_aggregated[sn]['gmv'] += float(o.total_amount)
            shift_aggregated[sn]['comm'] += float(o.commission_amount)
            
    shift_summary_list = [
        ShiftSummary(shift_name=k, orders=v['orders'], gmv=v['gmv'], commission=v['comm'])
        for k,v in shift_aggregated.items()
    ]
    
    # 6. Dependency Risk
    risks = []
    if strongest_accounts and total_gmv_day > 0:
        top_share = strongest_accounts[0].gmv / total_gmv_day
        if top_share > 0.6:
            risks.append({"type": "account", "message": f"Akun {strongest_accounts[0].name} mendominasi {round(top_share*100)}% GMV!"})

    # 7. Action Items
    actions = []
    if warnings:
        actions.append(f"Cek {len(warnings)} produk drop tajam, pertimbangkan ganti script/jam live.")
    if top_products:
        p = top_products[0]
        actions.append(f"Push produk '{p.product_name}' lebih sering, profitnya tinggi! 🔥")
    
    min_shift = min(shift_aggregated.items(), key=lambda x: x[1]['orders'])
    actions.append(f"{min_shift[0]} orderan sepi, coba strategi flash sale atau ganti host opening.")
    
    return DailyInsightsResponse(
        date=date_str,
        warnings={"products_drop_sharp": warnings},
        top_profit_products=top_products,
        strongest_accounts=strongest_accounts,
        host_ranking=host_ranking,
        shift_summary=shift_summary_list,
        dependency_risk=risks,
        action_items=actions
    )
