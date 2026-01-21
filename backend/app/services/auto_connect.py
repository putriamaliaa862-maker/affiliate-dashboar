"""
Auto Connect Service Layer
Handles account resolution, UPSERT, and sync logging for Chrome Extension
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import json
import logging

from app.models.user import User
from app.models.shopee_account import ShopeeAccount
from app.models.shopee_account_assignment import ShopeeAccountAssignment
from app.models.studio import Studio

logger = logging.getLogger(__name__)


class AutoConnectService:
    """Service for Auto Connect account management"""
    
    @staticmethod
    def resolve_account_identifier(account_info: Dict[str, Any], payload: Dict[str, Any]) -> str:
        """
        Resolve unique account identifier from payload.
        
        Priority order:
        1. account_id (most reliable)
        2. shop_id
        3. shop_name (normalized)
        4. username
        5. Extract from data.affiliate_dashboard
        6. Extract from data.live_streaming
        7. Extract from page_url if present
        8. REJECT with error (NO MORE "unknown" fallback)
        
        Returns:
            Unique account identifier string
        """
        # Try account_id first
        account_id = account_info.get('account_id') or account_info.get('shopee_account_id')
        if account_id and str(account_id).strip() and str(account_id).strip().lower() != 'unknown':
            logger.info(f"[AutoConnect] Resolved from account_id: {account_id}")
            return str(account_id).strip()
        
        # Try shop_id
        shop_id = account_info.get('shop_id')
        if shop_id and str(shop_id).strip():
            logger.info(f"[AutoConnect] Resolved from shop_id: {shop_id}")
            return f"shop_{str(shop_id).strip()}"
        
        # Try shop_name (normalize to ID format)
        shop_name = account_info.get('shop_name')
        if shop_name and str(shop_name).strip() and str(shop_name).strip().lower() not in ['unknown', 'unknown shop']:
            normalized = str(shop_name).strip().lower().replace(' ', '_').replace('-', '_')
            logger.info(f"[AutoConnect] Resolved from shop_name: {shop_name} -> {normalized}")
            return f"name_{normalized}"
        
        # Try username
        username = account_info.get('username')
        if username and str(username).strip() and str(username).strip().lower() != 'unknown':
            logger.info(f"[AutoConnect] Resolved from username: {username}")
            return f"user_{str(username).strip()}"
        
        # NEW: Try extracting from payload data
        payload_data = payload.get('data', {})
        
        # Check affiliate_dashboard data
        if 'affiliate_dashboard' in payload_data:
            aff_data = payload_data['affiliate_dashboard']
            if isinstance(aff_data, dict):
                aff_shop = aff_data.get('shop_name') or aff_data.get('username')
                if aff_shop and str(aff_shop).strip():
                    logger.info(f"[AutoConnect] Resolved from affiliate_dashboard: {aff_shop}")
                    return f"aff_{str(aff_shop).strip()}"
        
        # Check live_streaming data
        if 'live_streaming' in payload_data:
            live_data = payload_data['live_streaming']
            if isinstance(live_data, dict):
                live_shop = live_data.get('shop_name') or live_data.get('account_name')
                if live_shop and str(live_shop).strip():
                    logger.info(f"[AutoConnect] Resolved from live_streaming: {live_shop}")
                    return f"live_{str(live_shop).strip()}"
        
        # Try extracting from page_url in payload
        page_url = payload.get('url') or payload.get('page_url')
        if page_url:
            # Try to extract shop name/id from URL
            import re
            
            # Priority 1: Extract live_id from creator dashboard URL
            live_match = re.search(r'/dashboard/live/(\d+)', str(page_url))
            if live_match:
                live_id = live_match.group(1)
                account_identifier = f"live_{live_id}"
                logger.info(f"[AutoConnect] Resolved from live URL: {account_identifier}")
                return account_identifier
            
            # Priority 2: Extract shop identifier from URL
            match = re.search(r'/shop/([^/]+)', str(page_url))
            if match:
                shop_identifier = match.group(1)
                logger.info(f"[AutoConnect] Resolved from URL: {shop_identifier}")
                return f"url_{shop_identifier}"
        
        # REJECT: No valid identifier found
        logger.error(f"[AutoConnect] FAILED to resolve account identifier from payload: {account_info}")
        raise ValueError("Missing account identity from extension payload. Please ensure shop_name or account_id is sent.")
    
    @staticmethod
    def get_display_name(account_info: Dict[str, Any]) -> str:
        """Get user-friendly display name for account"""
        shop_name = account_info.get('shop_name')
        
        # If shop_name looks like "Shopee Live 191136817", use it
        if shop_name and str(shop_name).strip():
            return str(shop_name).strip()
        
        # Fallback to other fields
        return (
            account_info.get('username') or 
            account_info.get('account_id') or 
            "Unnamed Account"
        )
    
    @staticmethod
    def ensure_studio_exists(db: Session, user: User) -> int:
        """
        Ensure a studio exists for the user.
        
        Returns:
            studio_id to use
        """
        # Try to find any existing studio
        existing_studio = db.query(Studio).first()
        if existing_studio:
            logger.info(f"[AutoConnect] Using existing studio_id: {existing_studio.id}")
            return existing_studio.id
        
        # Create default studio if none exists
        logger.warning("[AutoConnect] No studio found, creating default studio")
        default_studio = Studio(
            name="Default Studio",
            description="Auto-created for extension sync",
            is_active=True
        )
        db.add(default_studio)
        db.flush()  # Get ID without committing yet
        logger.info(f"[AutoConnect] Created default studio_id: {default_studio.id}")
        return default_studio.id
    
    @staticmethod
    def upsert_shopee_account(
        db: Session,
        account_identifier: str,
        display_name: str,
        studio_id: int
    ) -> Tuple[ShopeeAccount, bool]:
        """
        Create or update shopee account.
        
        Returns:
            (ShopeeAccount, was_created: bool)
        """
        # Try to find existing account by shopee_account_id
        existing = db.query(ShopeeAccount).filter(
            ShopeeAccount.shopee_account_id == account_identifier
        ).first()
        
        if existing:
            # Update existing account
            existing.account_name = display_name
            existing.last_synced_at = datetime.utcnow()
            existing.is_active = True
            logger.info(f"[AutoConnect] Updated existing account_id={existing.id}, identifier={account_identifier}")
            db.flush()
            return (existing, False)
        
        # Create new account
        new_account = ShopeeAccount(
            studio_id=studio_id,
            account_name=display_name,
            shopee_account_id=account_identifier,
            last_synced_at=datetime.utcnow(),
            is_active=True
        )
        db.add(new_account)
        db.flush()
        logger.info(f"[AutoConnect] Created new account_id={new_account.id}, identifier={account_identifier}, name={display_name}")
        return (new_account, True)
    
    @staticmethod
    def ensure_assignment(
        db: Session,
        user: User,
        shopee_account: ShopeeAccount,
        set_as_default: bool = False
    ) -> Tuple[ShopeeAccountAssignment, bool]:
        """
        Ensure assignment exists between user and account.
        
        Args:
            set_as_default: If True, set this as user's default account (for identity sync)
        
        Returns:
            (ShopeeAccountAssignment, was_created: bool)
        """
        # Try to find existing assignment
        existing = db.query(ShopeeAccountAssignment).filter(
            ShopeeAccountAssignment.user_id == user.id,
            ShopeeAccountAssignment.shopee_account_id == shopee_account.id
        ).first()
        
        if existing:
            # Update is_default if requested
            if set_as_default and not existing.is_default:
                # Clear other default assignments first
                db.query(ShopeeAccountAssignment).filter(
                    ShopeeAccountAssignment.user_id == user.id,
                    ShopeeAccountAssignment.is_default == True
                ).update({'is_default': False})
                
                existing.is_default = True
                db.flush()
                logger.info(f"[AutoConnect] Set account_id={shopee_account.id} as default for user_id={user.id}")
            
            logger.info(f"[AutoConnect] Assignment exists: user_id={user.id}, account_id={shopee_account.id}")
            return (existing, False)
        
        # Create new assignment
        role_scope = user.role if user.role in ['owner', 'supervisor', 'partner', 'leader', 'host'] else 'viewer'
        
        # If set_as_default, clear other defaults first
        if set_as_default:
            db.query(ShopeeAccountAssignment).filter(
                ShopeeAccountAssignment.user_id == user.id,
                ShopeeAccountAssignment.is_default == True
            ).update({'is_default': False})
        
        new_assignment = ShopeeAccountAssignment(
            user_id=user.id,
            shopee_account_id=shopee_account.id,
            role_scope=role_scope,
            is_default=set_as_default
        )
        db.add(new_assignment)
        db.flush()
        logger.info(f"[AutoConnect] Created assignment: user_id={user.id}, account_id={shopee_account.id}, role={role_scope}, default={set_as_default}")
        return (new_assignment, True)
    
    @staticmethod
    def get_user_default_account(db: Session, user_id: int) -> Optional[ShopeeAccount]:
        """
        Get user's default account (set via Connect Account flow).
        
        Returns:
            ShopeeAccount if default exists, None otherwise
        """
        assignment = db.query(ShopeeAccountAssignment).filter(
            ShopeeAccountAssignment.user_id == user_id,
            ShopeeAccountAssignment.is_default == True
        ).first()
        
        if assignment:
            logger.info(f"[AutoConnect] Found default account for user_id={user_id}: account_id={assignment.shopee_account_id}")
            return assignment.shopee_account
        
        logger.warning(f"[AutoConnect] No default account for user_id={user_id}")
        return None
    
    @staticmethod
    def resolve_account_id(
        db: Session,
        user: User,
        payload: Dict[str, Any]
    ) -> str:
        """
        Resolve which account_id to use for this sync.
        
        Priority:
        1. User's default account (from Connect Account)
        2. Payload account_id (if valid and not auto/live)
        3. REJECT - don't create auto accounts anymore
        
        Returns:
            Resolved account identifier
        """
        # Priority 1: User's default account
        default_account = AutoConnectService.get_user_default_account(db, user.id)
        if default_account:
            logger.info(f"[AutoConnect] Using default account: {default_account.shopee_account_id}")
            return default_account.shopee_account_id
        
        # Priority 2: Payload account_id (if not auto-generated)
        account_info = payload.get('account', {})
        payload_account_id = account_info.get('account_id')
        
        if payload_account_id:
            # Reject auto-generated IDs
            if str(payload_account_id).startswith(('auto_', 'live_', 'unknown_')):
                logger.warning(f"[AutoConnect] Rejecting auto-generated account_id: {payload_account_id}")
            else:
                logger.info(f"[AutoConnect] Using payload account_id: {payload_account_id}")
                return str(payload_account_id)
        
        # REJECT: No valid account
        logger.error(f"[AutoConnect] No valid account found for user_id={user.id}")
        raise ValueError("No connected account found. Please use Connect Account first.")
    
    @staticmethod
    def log_sync(
        db: Session,
        user_id: int,
        account_id: int,
        payload_type: str,
        success: bool,
        raw_payload: Dict[str, Any],
        error_message: Optional[str] = None
    ):
        """
        Log sync activity for debugging and audit.
        
        Note: Stores in activity_logs for now.
        TODO: Create dedicated shopee_sync_logs table if needed.
        """
        from app.models.activity_log import ActivityLog
        
        # Build sync details (use new_value field which accepts JSON)
        sync_details = {
            'payload_type': payload_type,
            'success': success,
            'account_id': account_id,
            'raw_payload': raw_payload
        }
        
        if error_message:
            sync_details['error'] = error_message
        
        log = ActivityLog(
            user_id=user_id,
            action='extension_auto_connect_sync',
            entity_type='shopee_account',
            entity_id=account_id,
            new_value=sync_details  # FIXED: Use new_value instead of details
        )
        db.add(log)
        logger.info(f"[AutoConnect] Logged sync: user_id={user_id}, account_id={account_id}, success={success}")
