"""
TECHGURU ElevateCRM Database Configuration
"""
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize engines as None - will be created when database is available
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None


def initialize_database():
    """Initialize database connections when ready"""
    global engine, async_engine, SessionLocal, AsyncSessionLocal
    
    try:
        # Create sync engine for migrations
        engine = create_engine(
            settings.DATABASE_URL,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            echo=settings.DEBUG
        )

        # Create async engine for app usage
        async_engine = create_async_engine(
            settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            echo=settings.DEBUG
        )

        # Session makers
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        AsyncSessionLocal = async_sessionmaker(
            async_engine, class_=AsyncSession, expire_on_commit=False
        )
        
        logger.info("Database connections initialized")
        return True
    except Exception as e:
        logger.warning(f"Database not available: {e}")
        return False


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


async def get_async_session():
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def set_tenant_context(session, tenant_id: str):
    """Set tenant context for RLS in database session"""
    if not tenant_id:
        logger.warning("No tenant_id provided for RLS context")
        return
        
    try:
        # Set the tenant context for this session
        await session.execute(
            text("SELECT set_tenant_context(:tenant_id)"),
            {"tenant_id": tenant_id}
        )
        logger.debug(f"Set tenant context to {tenant_id}")
    except Exception as e:
        logger.error(f"Failed to set tenant context: {e}")
        # Don't raise - allow queries to continue but they may fail due to RLS


async def get_tenant_session(tenant_id: str):
    """Get async database session with tenant context set"""
    async with AsyncSessionLocal() as session:
        try:
            # Set tenant context for RLS
            await set_tenant_context(session, tenant_id)
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_session():
    """Get sync database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def create_tables():
    """Create database tables"""
    if not initialize_database():
        logger.warning("Skipping table creation - database not available")
        return
        
    try:
        # Import all models to ensure they're registered
        from app.models import Company, User, Contact, Product, Order, Integration
        
        async with async_engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        # Don't raise - allow app to start without database


# Dependency to get database session
def get_db():
    """Dependency to get database session"""
    if SessionLocal is None:
        initialize_database()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Async dependency to get async database session  
async def get_async_session():
    """Dependency to get async database session"""
    if AsyncSessionLocal is None:
        initialize_database()
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
