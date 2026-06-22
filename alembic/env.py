import os
from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, pool
from dotenv import load_dotenv
from db import Base

# Load environment variables
load_dotenv()

# The asynchronous PostgreSQL database URL for your app
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", "postgresql+asyncpg://postgres:1234@localhost:5432/lenoymed")

# The synchronous PostgreSQL database URL for Alembic
SYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("asyncpg", "psycopg2")

# Configure Alembic with the right settings
config = context.config
config.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)  # Use synchronous DB URL for Alembic

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target_metadata to your model's MetaData
target_metadata = Base.metadata

# Sync engine for Alembic migrations (Alembic needs a synchronous engine)
sync_engine = create_engine(SYNC_DATABASE_URL, poolclass=pool.NullPool)

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=SYNC_DATABASE_URL,  # Use the sync database URL here for offline migrations
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    with sync_engine.connect() as connection:  # Use the sync engine for migrations
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

# Run migrations based on the mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
