from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Database URL
SQLALCHEMY_DATABASE_URL = settings.database_url

# Create engine with Supabase optimizations if using Supabase
if settings.use_supabase:
    # Supabase uses connection pooling, so we need to configure accordingly
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=10,  # Number of connections to maintain in pool
        max_overflow=20,  # Max connections beyond pool_size
        pool_pre_ping=True,  # Verify connections before using (important for Supabase)
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=settings.debug  # Log SQL queries in debug mode
    )
else:
    # Standard PostgreSQL/SQLite configuration
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {},
        echo=settings.debug
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
