from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import settings

# Retrieve the asynchronous database connection URL from application settings
ASYNC_DATABASE_URL = settings.ASYNC_DATABASE_URL
if not ASYNC_DATABASE_URL:
    raise RuntimeError("ASYNC_DATABASE_URL is not configured")

# Initialize the asynchronous SQLAlchemy engine
# pool_pre_ping=True enables connectivity checks for pooled connections
async_engine = create_async_engine(ASYNC_DATABASE_URL, pool_pre_ping=True)

# Create a session factory for generating new AsyncSession instances
# expire_on_commit=False prevents objects from being detached after commit
AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)


async def get_db():
    """
    Dependency provider for database sessions.
    Yields an active session and ensures it is closed after use.
    """
    async with AsyncSessionLocal() as db:
        yield db
