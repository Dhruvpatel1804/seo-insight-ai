# Import asyncio for running async functions in sync context
import asyncio
from util.common import logger

# Import SQLAlchemy async components for database operations
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from core.config import settings
from worker.celery_app import celery_app

# Create async database engine with NullPool (no connection pooling)
# NullPool is used to avoid connection pool issues in worker processes
worker_engine = create_async_engine(settings.ASYNC_DATABASE_URL, poolclass=NullPool)

# Create async session factory for database operations
# expire_on_commit=False keeps objects in memory after commit
AsyncSessionLocal = async_sessionmaker(worker_engine, expire_on_commit=False, class_=AsyncSession)


@celery_app.task(name="worker.tasks.database_healthcheck", acks_late=True, max_retries=0)
def database_healthcheck():
    try:
        # Run the async function in the current event loop
        asyncio.run(_database_healthcheck())
    except Exception as e:
        logger.error(f"Error in database healthcheck, error: {str(e)}")
        raise e


# Async function that performs the actual token refresh
async def _database_healthcheck():
    """
    Check the health status of Postgres and Redis databases.
    """
    # 1. Check Postgres Health
    try:
        async with AsyncSessionLocal() as session:
            # Simple query to check if the database is responsive
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
            logger.info("Postgres health check: SUCCESS")
    except Exception as e:
        logger.error(f"Postgres health check: FAILED, error: {str(e)}")
        raise e

    # 2. Check Redis Health
    try:
        import redis.asyncio as redis
        redis_client = redis.from_url(settings.CELERY_BROKER_URL)
        ping_res = await redis_client.ping()
        if ping_res:
            logger.info("Redis health check: SUCCESS")
        else:
            logger.error("Redis health check: FAILED (No response)")
            raise Exception("Redis ping failed")
        await redis_client.aclose()
    except Exception as e:
        logger.error(f"Redis health check: FAILED, error: {str(e)}")
        raise e
