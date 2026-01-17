from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application Settings"""
    
    # Database
    database_url: str = "postgresql://user:password@localhost/affiliate_dashboard"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Shopee API
    shopee_api_base_url: str = "https://partner.shopeemobile.com/api/v2"
    shopee_partner_id: Optional[str] = None
    shopee_partner_key: Optional[str] = None
    shopee_sync_api_key: Optional[str] = None  # For Chrome Extension background sync
    access_code: Optional[str] = None  # For Chrome Extension popup manual actions
    
    # Application
    app_name: str = "Affiliate Dashboard"
    app_version: str = "0.1.0"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
