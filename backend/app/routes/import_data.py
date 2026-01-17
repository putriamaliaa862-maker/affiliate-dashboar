"""
CSV Import routes for Orders/Commissions
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import io
import numpy as np

from app.database import get_db
from app.models.order import Order
from app.models.shopee_account import ShopeeAccount
from app.models.user import User
from app.auth.dependencies import get_current_user, require_role

router = APIRouter()

# Schemas
class ImportPreviewResponse(BaseModel):
    detected_type: str
    headers: List[str]
    sample_rows: List[Dict[str, Any]]
    suggested_mapping: Dict[str, str]
    total_rows: int
    warnings: List[str]

class ImportExecuteRequest(BaseModel):
    shop_id: int
    import_type: str # 'commission' | 'sales'
    mapping: Dict[str, str]
    rows: List[Dict[str, Any]] # Passed from frontend for simplicity in this MVP, or re-upload file in prod

class ImportResult(BaseModel):
    inserted: int
    updated: int
    skipped: int
    failed: int
    failed_rows: List[Dict[str, Any]]

# Helper to normalize dates
def parse_date(date_str: Any) -> Optional[datetime]:
    if not date_str or pd.isna(date_str):
        return None
    
    date_str = str(date_str).strip()
    
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
            
    return None

# Helper to normalize currency
def parse_currency(val: Any) -> float:
    if not val or pd.isna(val):
        return 0.0
    
    if isinstance(val, (int, float)):
        return float(val)
        
    s = str(val).strip()
    # Remove currency symbols and separators
    s = s.replace('Rp', '').replace('.', '').replace(',', '.')
    try:
        return float(s)
    except:
        return 0.0

@router.post("/csv/preview", response_model=ImportPreviewResponse)
async def preview_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("admin"))
):
    """
    Parse CSV, detect headers, show preview, suggest mapping
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "File must be CSV")
        
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Replace NaN with None for JSON compatibility
        df = df.replace({np.nan: None})
        
        headers = list(df.columns)
        sample = df.head(10).to_dict(orient='records')
        
        # Smart Mapping Logic
        mapping = {}
        detected_type = "unknown"
        
        # Keywords for mapping
        map_rules = {
            "order_id": ["no. pesanan", "order id", "order no", "nomor pesanan"],
            "order_time": ["waktu pesanan", "order time", "waktu pembayaran", "paid time"],
            "gmv": ["total pembayaran", "total amount", "gmv", "harga asli"],
            "commission_amount": ["komisi", "commission", "jumlah komisi", "total komisi"],
            "payout_status": ["status", "status pembayaran"],
            "paid_at": ["waktu pelunasan", "payout date", "paid time"]
        }
        
        score_sales = 0
        score_commission = 0
        
        for field, keywords in map_rules.items():
            for header in headers:
                if any(k in header.lower() for k in keywords):
                    mapping[field] = header
                    if field in ["gmv", "order_time"]:
                        score_sales += 1
                    if field in ["commission_amount", "payout_status"]:
                        score_commission += 1
                    break
        
        if score_commission > score_sales:
            detected_type = "commission"
        elif score_sales > 0:
            detected_type = "sales"
            
        return ImportPreviewResponse(
            detected_type=detected_type,
            headers=headers,
            sample_rows=sample,
            suggested_mapping=mapping,
            total_rows=len(df),
            warnings=[]
        )
        
    except Exception as e:
        raise HTTPException(400, f"Failed to parse CSV: {str(e)}")

@router.post("/csv/execute", response_model=ImportResult)
async def execute_import(
    request: ImportExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Execute import with mapping
    """
    # Verify shop
    shop = db.query(ShopeeAccount).filter(ShopeeAccount.id == request.shop_id).first()
    if not shop:
        raise HTTPException(404, "Shopee Account not found")
    
    stats = {"inserted": 0, "updated": 0, "skipped": 0, "failed": 0, "failed_rows": []}
    
    for idx, row in enumerate(request.rows):
        try:
            # Check required fields via mapping
            order_id_col = request.mapping.get("order_id")
            if not order_id_col or not row.get(order_id_col):
                stats["skipped"] += 1
                continue
                
            raw_order_id = str(row[order_id_col]).strip()
            
            # Extract data
            order_time = None
            if request.mapping.get("order_time"):
                order_time = parse_date(row.get(request.mapping["order_time"]))
            
            # If no date found, skip (required for DB)
            if not order_time and request.import_type == 'sales':
                 # Try to find existing order to keep date
                 pass
            elif not order_time:
                 # Default to now if really needed, but better to fail row
                 # Or skip if strictly sales import
                 if request.import_type != 'commission': # Commission import might rely on existing order
                     stats["failed"] += 1
                     stats["failed_rows"].append({"row_index": idx, "reason": "Missing Order Time", "raw": row})
                     continue

            gmv = 0.0
            if request.mapping.get("gmv"):
                gmv = parse_currency(row.get(request.mapping["gmv"]))
                
            commission = 0.0
            if request.mapping.get("commission_amount"):
                commission = parse_currency(row.get(request.mapping["commission_amount"]))
                
            # Upsert Logic
            existing = db.query(Order).filter(
                Order.order_id == raw_order_id
            ).first()
            
            if existing:
                # UPDATE
                # Only update if new value is valid/non-empty to avoid overwriting with nulls
                if gmv > 0:
                    existing.total_amount = gmv
                if commission > 0:
                    existing.commission_amount = commission
                
                # Update status/dates if provided
                if request.mapping.get("payout_status"):
                    status_val = str(row.get(request.mapping["payout_status"])).lower()
                    if 'lunas' in status_val or 'paid' in status_val:
                        existing.payout_status = 'paid'
                    elif 'valid' in status_val:
                        existing.payout_status = 'validating'
                    else:
                        existing.payout_status = 'pending'
                        
                if request.mapping.get("paid_at"):
                    paid_date = parse_date(row.get(request.mapping["paid_at"]))
                    if paid_date:
                        existing.paid_at = paid_date
                
                # Check link to shop - if different, warn/error? We assume provided shop_id is correct source
                # existing.shopee_account_id = request.shop_id 
                
                stats["updated"] += 1
            else:
                # INSERT
                if not order_time:
                     stats["failed"] += 1
                     stats["failed_rows"].append({"row_index": idx, "reason": "New order missing date", "raw": row})
                     continue
                     
                new_order = Order(
                    shopee_account_id=request.shop_id,
                    order_id=raw_order_id,
                    date=order_time,
                    total_amount=gmv,
                    commission_amount=commission,
                    status="completed", # Default
                    payout_status="pending" # Default
                )
                
                # Map extra fields
                if request.mapping.get("payout_status"):
                    status_val = str(row.get(request.mapping["payout_status"])).lower()
                    if 'lunas' in status_val or 'paid' in status_val:
                        new_order.payout_status = 'paid'
                    elif 'valid' in status_val:
                        new_order.payout_status = 'validating'
                        
                if request.mapping.get("paid_at"):
                    paid_date = parse_date(row.get(request.mapping["paid_at"]))
                    if paid_date:
                        new_order.paid_at = paid_date
                        
                db.add(new_order)
                stats["inserted"] += 1
                
        except Exception as e:
            stats["failed"] += 1
            stats["failed_rows"].append({"row_index": idx, "reason": str(e), "raw": row})
            
    db.commit()
    return stats
