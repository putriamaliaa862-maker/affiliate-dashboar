"""
Enhanced Shopee Scraper Sync Endpoint
- API Key authentication
- Proper account mapping
- Data storage to database (orders, ads_daily_spend, ads_daily_metrics)
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, Optional
from datetime import datetime, date
import logging
import re

from app.database import get_db
from app.config import settings
from app.models.shopee_account import ShopeeAccount
from app.models.order import Order
from app.models.ads import AdsDailySpend, AdsDailyMetrics
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/shopee-data", tags=["Shopee Scraper"])


class ShopeeDataSync(BaseModel):
    timestamp: str
    url: str
    type: str
    sessionToken: Optional[str] = None
    accountId: str
    payload: Dict[str, Any]


def verify_extension_auth(
    x_sync_key: Optional[str] = Header(None),
    x_access_code: Optional[str] = Header(None)
):
    """
    Verify authentication from extension
    Supports BOTH:
    - x-sync-key: for background auto-sync (service worker)
    - x-access-code: for manual popup actions (Add Account, Send Performance)
    """
    # Check if either key is provided
    if not x_sync_key and not x_access_code:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication. Please provide x-sync-key or x-access-code header."
        )
    
    # Verify Sync API Key (background auto-sync)
    if x_sync_key:
        if not settings.shopee_sync_api_key:
            logger.warning("SHOPEE_SYNC_API_KEY not configured - sync endpoint is unsecured!")
            return True
        
        if x_sync_key == settings.shopee_sync_api_key:
            logger.info("Authenticated via Sync API Key (background)")
            return True
    
    # Verify Access Code (popup manual actions)
    if x_access_code:
        if not settings.access_code:
            logger.warning("ACCESS_CODE not configured - sync endpoint is unsecured!")
            return True
        
        if x_access_code == settings.access_code:
            logger.info("Authenticated via Access Code (popup)")
            return True
    
    # If we reach here, authentication failed
    logger.warning(f"Invalid authentication attempt")
    raise HTTPException(
        status_code=401,
        detail="Invalid authentication credentials. Please check your extension settings."
    )


def extract_shop_name(data: ShopeeDataSync) -> str:
    """
    Extract shop name from payload with fallback chain:
    1. payload.shop_name
    2. payload.shop_username
    3. payload.account_name
    4. Parse from URL
    5. accountId
    6. "unknown"
    """
    payload = data.payload
    
    # Try direct fields
    if payload.get("shop_name"):
        return str(payload["shop_name"]).strip()
    
    if payload.get("shop_username"):
        return str(payload["shop_username"]).strip()
    
    if payload.get("account_name"):
        return str(payload["account_name"]).strip()
    
    # Try to parse from URL
    if data.url:
        # Pattern: shopee.co.id/shop/{shop_name}
        match = re.search(r'/shop/([^/?]+)', data.url)
        if match:
            return match.group(1).strip()
        
        # Pattern: seller.shopee.co.id/{shop_name}
        match = re.search(r'seller\.shopee\.co\.id/([^/?]+)', data.url)
        if match:
            return match.group(1).strip()
    
    # Fallback to accountId
    if data.accountId and data.accountId != "unknown":
        return data.accountId.strip()
    
    return "unknown"


def find_or_create_account(db: Session, data: ShopeeDataSync, shop_name: str) -> ShopeeAccount:
    """
    Find existing account or create new one
    """
    # Try to find by shopee_account_id
    account = db.query(ShopeeAccount).filter(
        ShopeeAccount.shopee_account_id == data.accountId
    ).first()
    
    if account:
        logger.info(f"Found existing account: {account.account_name} (ID: {account.id})")
        # Update session token if provided
        if data.sessionToken and data.sessionToken != account.access_token:
            account.access_token = data.sessionToken
            db.commit()
        return account
    
    # Try to find by account_name (fuzzy match)
    if shop_name != "unknown":
        account = db.query(ShopeeAccount).filter(
            func.lower(ShopeeAccount.account_name) == shop_name.lower()
        ).first()
        
        if account:
            logger.info(f"Found account by name match: {account.account_name}")
            # Update shopee_account_id if missing
            if not account.shopee_account_id:
                account.shopee_account_id = data.accountId
                db.commit()
            return account
    
    # Create new account
    logger.info(f"Creating new account: {shop_name}")
    account = ShopeeAccount(
        studio_id=1,  # Default studio
        account_name=shop_name,
        shopee_account_id=data.accountId,
        access_token=data.sessionToken,
        is_active=True
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    
    logger.info(f"Created new account: {account.account_name} (ID: {account.id})")
    return account


def save_transactions(db: Session, account: ShopeeAccount, transactions: list) -> tuple:
    """
    Save transactions to orders table
    Returns: (created_count, updated_count, skipped_count)
    """
    created = 0
    updated = 0
    skipped = 0
    
    for txn in transactions:
        if not txn.get("orderId"):
            skipped += 1
            continue
        
        # Check if order exists
        existing_order = db.query(Order).filter(
            Order.order_id == txn["orderId"]
        ).first()
        
        if existing_order:
            # Update if values changed
            changed = False
            if txn.get("amount") and existing_order.total_amount != txn["amount"]:
                existing_order.total_amount = txn["amount"]
                changed = True
            if txn.get("commission") and existing_order.commission_amount != txn["commission"]:
                existing_order.commission_amount = txn["commission"]
                changed = True
            if txn.get("status") and existing_order.status != txn["status"]:
                existing_order.status = txn["status"]
                changed = True
            
            if changed:
                existing_order.updated_at = datetime.utcnow()
                updated += 1
            else:
                skipped += 1
        else:
            # Create new order
            order_date = datetime.utcnow()
            if txn.get("date"):
                try:
                    order_date = datetime.fromisoformat(txn["date"].replace("Z", "+00:00"))
                except:
                    pass
            
            new_order = Order(
                shopee_account_id=account.id,
                order_id=txn["orderId"],
                total_amount=txn.get("amount", 0),
                commission_amount=txn.get("commission", 0),
                status=txn.get("status", "completed"),
                date=order_date,
                product_name=txn.get("product_name"),
                product_id=txn.get("product_id")
            )
            db.add(new_order)
            created += 1
    
    db.commit()
    return (created, updated, skipped)


def save_affiliate_metrics(db: Session, account: ShopeeAccount, payload: dict, sync_date: date) -> bool:
    """
    Save affiliate dashboard metrics to ads_daily_metrics
    Returns: True if saved/updated
    """
    # Check if metrics exist for today
    existing = db.query(AdsDailyMetrics).filter(
        AdsDailyMetrics.date == sync_date,
        AdsDailyMetrics.shopee_account_id == account.id
    ).first()
    
    revenue = payload.get("totalCommission") or payload.get("paidCommission", 0)
    
    if existing:
        # Update if values changed
        if revenue and existing.revenue_manual != revenue:
            existing.revenue_manual = revenue
            existing.created_at = datetime.now()
            db.commit()
            return True
        return False
    else:
        # Create new metrics
        metrics = AdsDailyMetrics(
            date=sync_date,
            shopee_account_id=account.id,
            revenue_manual=revenue,
            note=f"Auto-synced from extension at {datetime.now().strftime('%H:%M:%S')}"
        )
        db.add(metrics)
        db.commit()
        return True


def save_live_streaming_data(db: Session, account: ShopeeAccount, payload: dict, sync_date: date) -> bool:
    """
    Save live streaming data as ads spend (type: live)
    Returns: True if saved/updated
    """
    revenue = payload.get("revenue", 0)
    if not revenue:
        return False
    
    # Check if spend exists for today
    existing = db.query(AdsDailySpend).filter(
        AdsDailySpend.date == sync_date,
        AdsDailySpend.shopee_account_id == account.id,
        AdsDailySpend.spend_type == "live"
    ).first()
    
    if existing:
        # Update if revenue changed
        if existing.spend_amount != revenue:
            existing.spend_amount = revenue
            existing.created_at = datetime.now()
            db.commit()
            return True
        return False
    else:
        # Create new spend record
        spend = AdsDailySpend(
            date=sync_date,
            shopee_account_id=account.id,
            spend_amount=revenue,
            spend_type="live",
            note=f"Live streaming - {payload.get('viewers', 0)} viewers, {payload.get('duration', 'N/A')}"
        )
        db.add(spend)
        db.commit()
        return True


@router.post("/sync")
async def sync_shopee_data(
    data: ShopeeDataSync,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_extension_auth)  # Support both Sync Key and Access Code
):
    """
    Receive scraped data from Chrome Extension
    Requires X-Sync-Key header for authentication
    """
    try:
        # Extract shop name
        shop_name = extract_shop_name(data)
        
        # Find or create account
        account = find_or_create_account(db, data, shop_name)
        
        # Log sync event
        logger.info(f"Sync received: type={data.type}, account={account.account_name}, payload_keys={list(data.payload.keys())}")
        
        # Process data based on type
        created = 0
        updated = 0
        skipped = 0
        sync_date = date.today()
        
        if data.type == "transactions":
            transactions = data.payload.get("transactions", [])
            created, updated, skipped = save_transactions(db, account, transactions)
            logger.info(f"Transactions saved: created={created}, updated={updated}, skipped={skipped}")
        
        elif data.type == "affiliate_dashboard":
            saved = save_affiliate_metrics(db, account, data.payload, sync_date)
            if saved:
                updated = 1
            logger.info(f"Affiliate metrics saved: {saved}")
        
        elif data.type == "live_streaming":
            saved = save_live_streaming_data(db, account, data.payload, sync_date)
            if saved:
                updated = 1
            logger.info(f"Live streaming data saved: {saved}")
        
        else:
            logger.warning(f"Unknown sync type: {data.type}")
        
        return {
            "success": True,
            "type": data.type,
            "account_id": account.id,
            "account_name": account.account_name,
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "message": f"Data synced successfully for {account.account_name}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sync error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Sync failed: {str(e)}"
        )


@router.get("/status")
async def get_sync_status(_: bool = Depends(verify_extension_auth)):
    """
    Check sync service status
    Requires x-sync-key or x-access-code header
    """
    return {
        "status": "online",
        "message": "Shopee scraper endpoint ready",
        "api_key_required": bool(settings.shopee_sync_api_key),
        "access_code_required": bool(settings.access_code)
    }
