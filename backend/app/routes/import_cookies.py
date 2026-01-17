"""
Shopee Accounts - Import Cookies Endpoint
Handles "Add Account to Server" from extension popup
"""
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import logging
import re

from app.database import get_db
from app.models.shopee_account import ShopeeAccount
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/shopee-accounts", tags=["Shopee Accounts"])


class ImportCookiesRequest(BaseModel):
    """Request model for importing cookies"""
    platform: str
    account_name: str
    cookie_spc_ec: str
    cookie_spc_f: str
    source_url: str


def verify_access_code(x_access_code: Optional[str] = Header(None)):
    """Verify Access Code from extension popup"""
    if not settings.access_code:
        logger.warning("ACCESS_CODE not configured - import endpoint is unsecured!")
        return True
    
    if not x_access_code:
        raise HTTPException(
            status_code=401,
            detail="Missing x-access-code header. Please save Access Code in extension first."
        )
    
    if x_access_code != settings.access_code:
        logger.warning(f"Invalid Access Code attempt: {x_access_code[:4]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid Access Code. Please check your extension settings."
        )
    
    return True


def extract_shop_name_from_url(url: str) -> Optional[str]:
    """Extract shop name from Shopee URL"""
    if not url:
        return None
    
    # Try seller.shopee.co.id/portal/...
    match = re.search(r'seller\.shopee\.co\.id/portal/shop/(\d+)', url)
    if match:
        return f"shop_{match.group(1)}"
    
    # Try affiliate.shopee.co.id
    match = re.search(r'affiliate\.shopee\.co\.id', url)
    if match:
        return "affiliate_account"
    
    return None


@router.post("/import-cookies")
async def import_cookies(
    request: ImportCookiesRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_access_code)
):
    """
    Import Shopee cookies and create/update account
    Called from extension popup "Add Account to Server" button
    """
    try:
        logger.info(f"Import cookies request from: {request.source_url}")
        
        # Extract shop name (priority order)
        shop_name = None
        
        # 1. Use provided account_name if not "Auto-detected"
        if request.account_name and request.account_name != "Auto-detected":
            shop_name = request.account_name.strip()
        
        # 2. Try to extract from URL
        if not shop_name:
            shop_name = extract_shop_name_from_url(request.source_url)
        
        # 3. Fallback to platform + timestamp
        if not shop_name:
            from datetime import datetime
            shop_name = f"{request.platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Detected shop name: {shop_name}")
        
        # Check if account exists (by cookies or name)
        existing_account = db.query(ShopeeAccount).filter(
            (ShopeeAccount.account_name == shop_name) |
            (ShopeeAccount.access_token == request.cookie_spc_ec)
        ).first()
        
        if existing_account:
            # Update existing account
            logger.info(f"Updating existing account: {existing_account.account_name} (ID: {existing_account.id})")
            existing_account.access_token = request.cookie_spc_ec
            existing_account.refresh_token = request.cookie_spc_f
            existing_account.is_active = True
            db.commit()
            db.refresh(existing_account)
            
            return {
                "success": True,
                "account_id": existing_account.id,
                "account_name": existing_account.account_name,
                "message": f"Account '{existing_account.account_name}' updated successfully"
            }
        else:
            # Create new account
            logger.info(f"Creating new account: {shop_name}")
            new_account = ShopeeAccount(
                studio_id=1,  # Default studio
                account_name=shop_name,
                access_token=request.cookie_spc_ec,
                refresh_token=request.cookie_spc_f,
                is_active=True
            )
            db.add(new_account)
            db.commit()
            db.refresh(new_account)
            
            logger.info(f"Created new account: {new_account.account_name} (ID: {new_account.id})")
            
            return {
                "success": True,
                "account_id": new_account.id,
                "account_name": new_account.account_name,
                "message": f"Account '{new_account.account_name}' added successfully"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Import cookies error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import cookies: {str(e)}"
        )
