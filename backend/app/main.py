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
    analytics,
    bonus,
    import_data,
    import_data,
    insights,
    ads,
    dashboard,
    import_cookies,
    live_products
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
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


# Include routers
# Authentication & User Management
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(activity_logs.router, prefix="/api")

# Business Logic
app.include_router(studio.router, prefix="/api/studios", tags=["Studios"])
app.include_router(employee.router, prefix="/api/employees", tags=["Employees"])
app.include_router(attendance.router, prefix="/api/attendances", tags=["Attendance"])
app.include_router(shopee_account.router, prefix="/api/shopee-accounts", tags=["Shopee Accounts"])
app.include_router(commission.router, prefix="/api/commissions", tags=["Commissions"])
app.include_router(report.router, prefix="/api/reports", tags=["Reports"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(bonus.router, prefix="/api/bonus", tags=["Bonus"])
app.include_router(import_data.router, prefix="/api/import", tags=["Import"])
app.include_router(insights.router, prefix="/api/insights", tags=["Insights"])
app.include_router(ads.router) # /api/ads prefix is defined in the router itself
app.include_router(dashboard.router, prefix="/api") # Dashboard owner endpoint
app.include_router(import_cookies.router, prefix="/api") # Extension import cookies
app.include_router(live_streaming.router)
app.include_router(shopee_scraper.router, prefix="/api")
app.include_router(live_products.router, prefix="/api")
