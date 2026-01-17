from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel
import csv
import io
import logging

from app.database import get_db
from app.models.order import Order
from app.models.shopee_account import ShopeeAccount
from app.models.user import User
from app.auth.dependencies import get_current_user, require_role
from app.core.permissions import verify_financial_access, apply_scope_restriction

# Setup logger
logger = logging.getLogger(__name__)

router = APIRouter()


class PayoutSummary(BaseModel):
    total_commission: float
    paid: float
    pending: float
    validating: float


class PayoutRow(BaseModel):
    order_id: str
    account_id: int
    account_name: str
    commission_amount: float
    payout_status: str  # paid, pending, validating
    payment_method: Optional[str]
    validated_at: Optional[datetime]
    completed_at: Optional[datetime]
    paid_at: Optional[datetime]
    date: datetime


class PayoutHistoryResponse(BaseModel):
    summary: PayoutSummary
    rows: List[PayoutRow]


class MarkPaidRequest(BaseModel):
    order_ids: List[str]
    payment_method: str = "transfer"


@router.get("/payout-history", response_model=PayoutHistoryResponse)
async def get_payout_history(
    request: Request,
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    status: Optional[str] = None,  # pending, paid, validating
    search: Optional[str] = None,
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get payout history with status filtering and summary cards.
    RBAC: Owner/Admin/Leader (Full), Host (Scoped to handled orders)
    """
    # RBAC Logic
    if not verify_financial_access(current_user, "payout-history"):
        raise HTTPException(
            status_code=403, 
            detail="You do not have permission to view payout history"
        )

    # Base query
    query = db.query(Order).join(
        ShopeeAccount, Order.shopee_account_id == ShopeeAccount.id
    ).filter(
        and_(
            func.date(Order.date) >= from_date,
            func.date(Order.date) <= to_date,
            Order.status == 'completed'
        )
    )

    # Calculate summary stats (ignoring status filter) - Optimized
    summary_query = db.query(
        func.sum(Order.commission_amount).label('total'),
        func.sum(case((Order.payout_status == 'paid', Order.commission_amount), else_=0)).label('paid'),
        func.sum(case((Order.payout_status == 'pending', Order.commission_amount), else_=0)).label('pending'),
        func.sum(case((Order.payout_status == 'validating', Order.commission_amount), else_=0)).label('validating')
    ).filter(
        and_(
            func.date(Order.date) >= from_date,
            func.date(Order.date) <= to_date,
            Order.status == 'completed'
        )
    )
    
    # Apply RBAC Scope
    query = apply_scope_restriction(query, current_user, Order)
    summary_query = apply_scope_restriction(summary_query, current_user, Order)

    if account_id:
        query = query.filter(Order.shopee_account_id == account_id)
        summary_query = summary_query.filter(Order.shopee_account_id == account_id)
        
    # Apply filters to main query
    if status and status != 'all':
        query = query.filter(Order.payout_status == status)
        
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Order.order_id.ilike(search_term),
                ShopeeAccount.account_name.ilike(search_term)
            )
        )
        
    rows = query.order_by(Order.date.desc()).limit(500).all()  # Limit for performance
    stats = summary_query.first()
    
    # Map Response
    response_rows = []
    for order in rows:
        response_rows.append(PayoutRow(
            order_id=order.order_id or f"ORDER-{order.id}",
            account_id=order.shopee_account_id,
            account_name=order.shopee_account.account_name if order.shopee_account else "Unknown",
            commission_amount=float(order.commission_amount or 0),
            payout_status=order.payout_status or 'pending',
            payment_method=order.payment_method,
            validated_at=order.validated_at,
            completed_at=order.date, # Using order date as completion date for now
            paid_at=order.paid_at,
            date=order.date
        ))
        
    # Handle case where stats might be None (if no rows match) or internal sums None
    total_val = stats.total if stats and stats.total else 0
    paid_val = stats.paid if stats and stats.paid else 0
    pending_val = stats.pending if stats and stats.pending else 0
    validating_val = stats.validating if stats and stats.validating else 0

    return PayoutHistoryResponse(
        summary=PayoutSummary(
            total_commission=float(total_val),
            paid=float(paid_val),
            pending=float(pending_val),
            validating=float(validating_val)
        ),
        rows=response_rows
    )


@router.post("/mark-paid")
async def mark_commissions_paid(
    payload: MarkPaidRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Bulk mark commissions as PAID
    """
    orders = db.query(Order).filter(Order.order_id.in_(payload.order_ids)).all()
    
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
        
    count = 0
    now = datetime.utcnow()
    
    for order in orders:
        if order.payout_status != 'paid':
            order.payout_status = 'paid'
            order.paid_at = now
            order.payment_method = payload.payment_method
            count += 1
            
    db.commit()
    
    return {"message": f"Successfully marked {count} orders as PAID"}


@router.get("/export-csv")
async def export_payout_csv(
    request: Request,
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    status: Optional[str] = None,
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export payout history as CSV
    """
    # RBAC Logic
    if not verify_financial_access(current_user, "export-csv"):
        raise HTTPException(status_code=403, detail="Forbidden")

    query = db.query(Order).join(ShopeeAccount).filter(
        and_(
            func.date(Order.date) >= from_date,
            func.date(Order.date) <= to_date,
            Order.status == 'completed'
        )
    )

    # Apply Scope Restriction
    query = apply_scope_restriction(query, current_user, Order)
    
    if account_id:
        query = query.filter(Order.shopee_account_id == account_id)
        
    if status and status != 'all':
        query = query.filter(Order.payout_status == status)
        
    results = query.order_by(Order.date.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'Order ID', 'Date', 'Account', 'Commission (Rp)', 
        'Status', 'Payment Method', 'Paid At'
    ])
    
    for order in results:
        writer.writerow([
            order.order_id,
            order.date.strftime('%Y-%m-%d %H:%M'),
            order.shopee_account.account_name if order.shopee_account else '-',
            f"{float(order.commission_amount):.2f}",
            order.payout_status.upper(),
            order.payment_method or '-',
            order.paid_at.strftime('%Y-%m-%d %H:%M') if order.paid_at else '-'
        ])
        
    output.seek(0)
    filename = f"payouts_{from_date}_{to_date}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
