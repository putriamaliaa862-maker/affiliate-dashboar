"""
Access Code Authentication Dependency
For Chrome Extension endpoints (no JWT required)
"""
from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User


async def verify_access_code(
    x_access_code: str = Header(None, alias="X-Access-Code"),
    db: Session = Depends(get_db)
) -> User:
    """
    Verify X-Access-Code header and return associated user.
    
    Used by extension endpoints instead of JWT authentication.
    Returns the user if code is valid and active.
    
    Args:
        x_access_code: Access code from X-Access-Code header
        db: Database session
    
    Returns:
        User object
    
    Raises:
        401: If header missing or code invalid
        403: If user account disabled
    """
    if not x_access_code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Access-Code header required. Generate code from Settings page."
        )
    
    # Find user by access code
    user = db.query(User).filter(User.access_code == x_access_code).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access code. Please check your code in Settings."
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled. Contact administrator."
        )
    
    return user
