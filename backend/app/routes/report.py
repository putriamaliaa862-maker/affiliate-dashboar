"""
Report generation routes using Order data with CSV export
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import csv
import io

from app.database import get_db
from app.models.user import User
from app.models.order import Order
from app.models.shopee_account import ShopeeAccount
from app.auth.dependencies import get_current_user, require_role
from pydantic import BaseModel

router = APIRouter(prefix="/api/reports", tags=["Reports"])


class ReportFilters(BaseModel):
    """Report filter parameters"""
    from_date: date
    to_date: date
    account_id: Optional[int] = None


class ReportRow(BaseModel):
    """Single report row"""
    date: str
    shop_name: str
    total_orders: int
    total_gmv: float
    total_commission: float


class ReportResponse(BaseModel):
    """Report generation response"""
    data: List[ReportRow]
    summary: dict


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    filters: ReportFilters,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("leader"))  # Admin & Leader only
):
    """
    Generate sales report with filters.
    
    **Permissions:** Leader or higher
    
    **Generates report showing:**
    - Date
    - Shop Name
    - Total Orders
    - Total GMV
    - Total Commission
    """
    # Build query - aggregate orders by date and account
    query = db.query(
        func.date(Order.date).label('date'),
        ShopeeAccount.account_name.label('shop_name'),
        func.count(Order.id).label('total_orders'),
        func.sum(Order.total_amount).label('total_gmv'),
        func.sum(Order.commission_amount).label('total_commission')
    ).join(
        ShopeeAccount, Order.shopee_account_id == ShopeeAccount.id
    ).filter(
        and_(
            func.date(Order.date) >= filters.from_date,
            func.date(Order.date) <= filters.to_date,
            Order.status == 'completed'  # Only completed orders
        )
    )
    
    # Apply optional filters
    if filters.account_id:
        query = query.filter(Order.shopee_account_id == filters.account_id)
    
    # Group by date and shop
    query = query.group_by(
        func.date(Order.date),
        ShopeeAccount.account_name
    ).order_by(func.date(Order.date).desc())
    
    results = query.all()
    
    # Transform to response format
    data = []
    total_orders = 0
    total_gmv = Decimal(0)
    total_commission = Decimal(0)
    
    for row in results:
        gmv = float(row.total_gmv) if row.total_gmv else 0
        commission = float(row.total_commission) if row.total_commission else 0
        orders = row.total_orders or 0
        
        data.append(ReportRow(
            date=str(row.date),
            shop_name=row.shop_name or "Unknown",
            total_orders=orders,
            total_gmv=gmv,
            total_commission=commission
        ))
        
        total_orders += orders
        total_gmv += Decimal(str(gmv))
        total_commission += Decimal(str(commission))
    
    return ReportResponse(
        data=data,
        summary={
            "total_orders": total_orders,
            "total_gmv": float(total_gmv),
            "total_commission": float(total_commission),
            "avg_order_value": float(total_gmv / total_orders) if total_orders > 0 else 0
        }
    )


@router.get("/export-csv")
async def export_csv(
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("leader"))  # Admin & Leader only
):
    """
    Export report as CSV file.
    
    **Permissions:** Leader or higher
    """
    # Build query (same as generate_report)
    query = db.query(
        func.date(Order.date).label('date'),
        ShopeeAccount.account_name.label('shop_name'),
        func.count(Order.id).label('total_orders'),
        func.sum(Order.total_amount).label('total_gmv'),
        func.sum(Order.commission_amount).label('total_commission')
    ).join(
        ShopeeAccount, Order.shopee_account_id == ShopeeAccount.id
    ).filter(
        and_(
            func.date(Order.date) >= from_date,
            func.date(Order.date) <= to_date,
            Order.status == 'completed'
        )
    )
    
    if account_id:
        query = query.filter(Order.shopee_account_id == account_id)
    
    query = query.group_by(
        func.date(Order.date),
        ShopeeAccount.account_name
    ).order_by(func.date(Order.date).desc())
    
    results = query.all()
    
    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Date',
        'Shop Name',
        'Total Orders',
        'Total GMV (Rp)',
        'Total Commission (Rp)'
    ])
    
    # Data rows
    for row in results:
        writer.writerow([
            str(row.date),
            row.shop_name or "Unknown",
            row.total_orders or 0,
            f"{float(row.total_gmv):,.2f}" if row.total_gmv else "0.00",
            f"{float(row.total_commission):,.2f}" if row.total_commission else "0.00"
        ])
    
    # Filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"sales_report_{timestamp}.csv"
    
    # Response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
