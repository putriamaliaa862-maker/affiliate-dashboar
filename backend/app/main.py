from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.database import Base, engine
from app.config import settings
from app.routes import (
    auth,
    users,
    activity_logs,
    studio,
    employee,
    attendance,
    shopee_account,
    commission,
    report,
    live_streaming,
    shopee_scraper,
    shopee_data,  # NEW: realtime sync
    shopee_data_sync,  # NEW PHASE 2: Auto Connect
    shopee_data_sync_supabase,  # NEW: Supabase staging table processor
    analytics,
    bonus,
    import_data,
    insights,
    ads,
    dashboard,
    import_cookies,
    live_products,
    premium_dashboard,  # NEW: Premium features
    bot_ingest  # NEW: 24H Playwright Bot
)

logger = logging.getLogger(__name__)

# Create tables (with error handling if database is down)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
except Exception as e:
    logger.warning(f"Could not create database tables: {e}. Database may be offline.")

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to Affiliate Dashboard API",
        "version": settings.app_version,
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "docs": "/docs"
    }


# Register all routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(activity_logs.router)
app.include_router(studio.router)
app.include_router(employee.router)
app.include_router(attendance.router)
app.include_router(shopee_account.router)
app.include_router(commission.router)
app.include_router(report.router)
app.include_router(live_streaming.router)
app.include_router(shopee_scraper.router)
app.include_router(shopee_data.router)
app.include_router(shopee_data_sync.router)  # NEW PHASE 2: Auto Connect
app.include_router(shopee_data_sync_supabase.router)  # NEW: Supabase staging processor
app.include_router(analytics.router)
app.include_router(bonus.router)
app.include_router(import_data.router)
app.include_router(insights.router)
app.include_router(ads.router)
app.include_router(dashboard.router)
app.include_router(import_cookies.router)
app.include_router(live_products.router)
app.include_router(premium_dashboard.router)  # NEW: Premium dashboard
app.include_router(bot_ingest.router)  # NEW: 24H Playwright Bot

