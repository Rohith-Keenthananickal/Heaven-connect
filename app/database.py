from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

# Convert MySQL URL to async
ASYNC_DATABASE_URL = settings.DATABASE_URL.replace("mysql+pymysql://", "mysql+aiomysql://")

# Create async database engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)

# Create sync database engine
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync session maker
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False
)

# Create base class for models
class Base(DeclarativeBase):
    pass


async def get_db():
    """Dependency to get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_db():
    """Dependency to get sync database session"""
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_async_engine():
    """Get the async database engine"""
    return engine