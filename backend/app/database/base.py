"""Database configuration and base models."""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from typing import AsyncGenerator

# Get database URL from Railway environment and convert for asyncpg
# Railway provides DATABASE_PUBLIC_URL, but we also check for DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DATABASE_PUBLIC_URL", "postgresql+asyncpg://localhost/garmin_ai_coach")
print(f"🔌 Original DATABASE_URL: {DATABASE_URL[:50]}...")

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    print(f"🔧 Converted to asyncpg: {DATABASE_URL[:50]}...")

# Create async engine with Railway-optimized settings
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging in development
    pool_size=5,          # Reduced for Railway limits
    max_overflow=10,      # Reduced for Railway limits
    pool_timeout=30,      # Connection timeout
    pool_recycle=3600,    # Recycle connections after 1 hour
    pool_pre_ping=True,   # Validate connections before use
    connect_args={
        "connect_timeout": 10,     # Connection timeout in seconds
        "command_timeout": 60,     # Command timeout in seconds
        "server_settings": {
            "jit": "off",          # Disable JIT for better compatibility
        }
    }
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """Base model class with common fields."""
    
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    session = None
    try:
        session = AsyncSessionLocal()
        # Test connection
        await session.execute(text("SELECT 1"))
        yield session
        await session.commit()
    except Exception as e:
        if session:
            await session.rollback()
        print(f"🚨 Database session error: {str(e)}")
        raise
    finally:
        if session:
            await session.close()


async def init_database():
    """Initialize database tables."""
    try:
        # Import all models to register them with Base.metadata
        from app.database.models import user, training_config, analysis
        
        # Test basic connection first
        async with engine.begin() as conn:
            # Test the connection
            result = await conn.execute(text("SELECT version()"))
            version = result.fetchone()
            print(f"🗄️ Connected to PostgreSQL: {version[0] if version else 'Unknown'}")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("🗄️ Database tables created successfully")
            
    except Exception as e:
        print(f"🚨 Database initialization failed: {str(e)}")
        print("📝 App will continue but database features may not work")
        # Don't raise the error - let the app start even if DB is down
        return False
    
    return True