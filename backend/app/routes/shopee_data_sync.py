"""
Shopee Data Sync Routes - FIXED VERSION
Main Auto Connect endpoint for Chrome Extension with proper UPSERT logic
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from app.database import get_db
from app.auth.access_code import verify_access_code
from app.models.user import User
from app.models.order import Order
from app.services.auto_connect import AutoConnectService
from app.routes.shopee_data_sync_helpers import _process_live_streaming

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/shopee-data", tags=["Shopee Data Sync"])


# ==================== SCHEMAS ====================

class AccountInfo(BaseModel):
    account_id: Optional[str] = None
    shop_id: Optional[str] = None
    shop_name: Optional[str] = None
    username: Optional[str] = None
    shopee_account_id: Optional[str] = None  # Alternative field name


class SyncRequest(BaseModel):
    account: AccountInfo
    type: str  # "transactions", "affiliate_dashboard", "live_streaming", "ads"
    data: Dict[str, Any]
    url: Optional[str] = None  # Page URL for additional context


class SyncResponse(BaseModel):
    success: bool
    user_id: int
    account_id: str  # The shopee_account_id (external identifier)
    db_account_id: int  # Our internal DB primary key
    account_created: bool
    assignment_created: bool
    message: str
    inserted: int = 0
    updated: int = 0


# ==================== ENDPOINTS ====================

@router.post("/sync", response_model=SyncResponse)
async def sync_data_from_extension(
    payload: SyncRequest,
    current_user: User = Depends(verify_access_code),
    db: Session = Depends(get_db)
):
    """
    Auto-connect endpoint for Chrome Extension.
    
    Auth: X-Access-Code header (NO JWT)
    
    Flow:
    1. Authenticate user via access code
    2. Resolve account identifier from payload
    3. UPSERT shopee_account (create if new, update if exists)
    4. UPSERT assignment (ensure user can access this account)
    5. Process data (orders, transactions, etc.)
    6. Log sync
    7. Return structured response
    """
    # ✅ ULTRA CLEAR LOGGING
    print("=" * 60)
    print("✅ SYNC HIT")
    print(f"User ID: {current_user.id}")
    print(f"Payload Type: {payload.type}")
    print(f"Account Info Keys: {list(payload.account.dict().keys())}")
    print(f"Account Info Values: {payload.account.dict()}")
    print(f"Data Keys: {list(payload.data.keys())}")
    
    # Debug specific data types
    if 'transactions' in payload.data:
        print(f"Transactions count: {len(payload.data.get('transactions', []))}")
        if payload.data['transactions']:
            print(f"Transaction sample: {payload.data['transactions'][0]}")
    
    if 'affiliate_dashboard' in payload.data:
        print(f"Affiliate Dashboard keys: {list(payload.data['affiliate_dashboard'].keys())}")
    
    if 'live_streaming' in payload.data:
        print(f"Live Streaming keys: {list(payload.data['live_streaming'].keys())}")
        print(f"Live Streaming data: {payload.data['live_streaming']}")
    
    print("=" * 60)
    
    logger.info(f"[SyncEndpoint] Received sync request from user_id={current_user.id}, type={payload.type}")
    
    try:
        # ✅ VALIDATION: Prioritize shopee_account_id, fallback to account_id
        account_id_from_payload = payload.account.shopee_account_id or payload.account.account_id
        
        print(f"Account ID resolved: {account_id_from_payload}")
        print(f"Shop Name: {payload.account.shop_name}")
        
        if not account_id_from_payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NOT_CONNECTED: Missing shopee_account_id or account_id. Please use Connect Account in extension first."
            )
        
        # Reject auto-generated IDs (except for identity sync)
        if payload.type != 'identity':
            if str(account_id_from_payload).startswith(('auto_', 'unknown_', 'live_')):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"NOT_CONNECTED: Invalid account_id '{account_id_from_payload}'. Please use Connect Account first. Auto-generated IDs not allowed."
                )
        
        # SPECIAL CASE: Identity sync (Connect Account flow)
        if payload.type == 'identity':
            # For identity, we MUST have account_id and shop_name
            account_id = payload.account.account_id or payload.data.get('account_id')
            shop_name = payload.account.shop_name or payload.data.get('shop_name')
            
            if not account_id:
                raise ValueError("Identity sync requires account_id")
            
            # Ensure studio exists
            studio_id = AutoConnectService.ensure_studio_exists(db, current_user)
            
            # Upsert account
            shopee_account, account_created = AutoConnectService.upsert_shopee_account(
                db=db,
                account_identifier=account_id,
                display_name=shop_name or account_id,
                studio_id=studio_id
            )
            
            # Create assignment and SET AS DEFAULT
            assignment, assignment_created = AutoConnectService.ensure_assignment(
                db=db,
                user=current_user,
                shopee_account=shopee_account,
                set_as_default=True  # ✅ SET AS DEFAULT!
            )
            
            # Log sync
            AutoConnectService.log_sync(
                db=db,
                user_id=current_user.id,
                account_id=shopee_account.id,
                payload_type='identity',
                success=True,
                raw_payload=payload.dict()
            )
            
            db.commit()
            
            print("=" * 60)
            print("✅ IDENTITY SYNC SUCCESS")
            print(f"Account ID: {account_id}")
            print(f"Account Name: {shop_name}")
            print(f"Set as DEFAULT: True")
            print("=" * 60)
            
            return SyncResponse(
                success=True,
                user_id=current_user.id,
                account_id=account_id,
                db_account_id=shopee_account.id,
                account_created=account_created,
                assignment_created=assignment_created,
                message=f"Identity synced. {shop_name} set as default account.",
                inserted=0,
                updated=0
            )
        
        # REGULAR SYNC: Use resolved account
        # Priority: User's default account > Payload account_id > REJECT
        resolved_account_id = AutoConnectService.resolve_account_id(
            db=db,
            user=current_user,
            payload={'account': payload.account.dict(), 'data': payload.data, 'url': payload.url}
        )
        
        print("=" * 60)
        print("✅ RESOLVED ACCOUNT")
        print(f"User ID: {current_user.id}")
        print(f"Payload Type: {payload.type}")
        print(f"Resolved Account ID: {resolved_account_id}")
        print("=" * 60)
        
        # Get display name
        display_name = AutoConnectService.get_display_name(payload.account.dict())
        
        logger.info(f"[SyncEndpoint] Resolved account - identifier={resolved_account_id}, display={display_name}")
        
        # STEP 2: Ensure studio exists (required for shopee_accounts FK)
        studio_id = AutoConnectService.ensure_studio_exists(db, current_user)
        
        # STEP 3: UPSERT shopee_account with resolved ID
        shopee_account, account_created = AutoConnectService.upsert_shopee_account(
            db=db,
            account_identifier=resolved_account_id,
            display_name=display_name,
            studio_id=studio_id
        )
        
        # STEP 4: UPSERT assignment (NOT default, only identity sets default)
        assignment, assignment_created = AutoConnectService.ensure_assignment(
            db=db,
            user=current_user,
            shopee_account=shopee_account,
            set_as_default=False  # Regular sync doesn't change default
        )
        
        # STEP 5: Process data based on type
        inserted = 0
        updated = 0
        live_rows = 0
        ads_rows = 0
        
        if payload.type in ["transactions", "affiliate_dashboard"]:
            inserted, updated = _process_orders(db, shopee_account.id, payload.data)
        elif payload.type == "live_streaming":
            # Save live streaming metrics
            live_rows = _process_live_streaming(db, shopee_account.id, payload.data)
        elif payload.type == "ads":
            # Future: Process ads data
            ads_rows = 0
        
        # STEP 6: Log sync
        AutoConnectService.log_sync(
            db=db,
            user_id=current_user.id,
            account_id=shopee_account.id,
            payload_type=payload.type,
            success=True,
            raw_payload=payload.dict()
        )
        
        # STEP 7: Commit all changes
        db.commit()
        
        logger.info(f"[SyncEndpoint] SUCCESS - account_id={shopee_account.id}, created={account_created}, orders={inserted+updated}, live={live_rows}")
        
        print("=" * 60)
        print("✅ SYNC SUCCESS")
        print(f"Account ID: {account_identifier}")
        print(f"Account Name: {display_name}")
        print(f"Orders Upserted: {inserted + updated}")
        print(f"Live Rows: {live_rows}")
        print("=" * 60)
        
        return SyncResponse(
            success=True,
            user_id=current_user.id,
            account_id=account_identifier,
            db_account_id=shopee_account.id,
            account_created=account_created,
            assignment_created=assignment_created,
            message=f"Synced successfully. Account: {display_name}. Orders: {inserted+updated}, Live: {live_rows}",
            inserted=inserted,
            updated=updated
        )
        
    except ValueError as e:
        # Account identity resolution failed
        db.rollback()
        logger.error(f"[SyncEndpoint] Account identity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"[SyncEndpoint] Database integrity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database constraint violation: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"[SyncEndpoint] Unexpected error: {e}")
        
        # Log failed sync
        try:
            AutoConnectService.log_sync(
                db=db,
                user_id=current_user.id,
                account_id=0,  # Unknown account
                payload_type=payload.type,
                success=False,
                raw_payload=payload.dict(),
                error_message=str(e)
            )
            db.commit()
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )


# ==================== HELPERS ====================

def _process_orders(db: Session, account_id: int, data: Dict[str, Any]) -> tuple:
    """
    Process order/transaction data.
    Returns: (inserted_count, updated_count)
    """
    inserted = 0
    updated = 0
    
    # Extract orders from data (format may vary)
    orders_data = data.get("orders", []) or data.get("transactions", []) or []
    
    logger.info(f"[ProcessOrders] Processing {len(orders_data)} orders for account_id={account_id}")
    
    for order_data in orders_data:
        order_id = order_data.get("order_id") or order_data.get("id")
        
        if not order_id:
            logger.warning(f"[ProcessOrders] Skipping order without ID")
            continue
        
        # Check if exists
        existing = db.query(Order).filter(Order.order_id == str(order_id)).first()
        
        if existing:
            # Update existing (only if new data has more info)
            if "total_amount" in order_data and order_data["total_amount"]:
                existing.total_amount = float(order_data["total_amount"])
            if "commission_amount" in order_data and order_data["commission_amount"]:
                existing.commission_amount = float(order_data["commission_amount"])
            if "status" in order_data:
                existing.status = order_data["status"]
            updated += 1
        else:
            # Create new
            try:
                order = Order(
                    shopee_account_id=account_id,
                    order_id=str(order_id),
                    total_amount=float(order_data.get("total_amount", 0)),
                    commission_amount=float(order_data.get("commission_amount", 0)),
                    date=_parse_date(order_data.get("date")),
                    status=order_data.get("status", "completed")
                )
                db.add(order)
                inserted += 1
            except Exception as e:
                logger.error(f"[ProcessOrders] Error creating order {order_id}: {e}")
                continue
    
    logger.info(f"[ProcessOrders] Result - inserted={inserted}, updated={updated}")
    return (inserted, updated)


def _parse_date(date_str: Optional[str]) -> datetime:
    """Parse date from various formats"""
    if not date_str:
        return datetime.utcnow()
    
    try:
        # Try ISO format first
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        try:
            # Try common formats
            from dateutil import parser
            return parser.parse(date_str)
        except:
            return datetime.utcnow()
