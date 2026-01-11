#!/usr/bin/env python3
"""
Database migration runner for Railway deployment.
This script runs Alembic migrations to update the database schema.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from alembic.config import Config
from alembic import command
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_database_url():
    """Get database URL from environment variables."""
    database_url = os.getenv("DATABASE_URL") or os.getenv("DATABASE_PUBLIC_URL")
    
    if not database_url:
        logger.error("DATABASE_URL environment variable is not set!")
        return None
    
    # Convert postgres:// to postgresql:// for SQLAlchemy
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    logger.info(f"Using database URL: {database_url.split('@')[0]}@[REDACTED]")
    return database_url


def run_migrations():
    """Run Alembic database migrations."""
    
    try:
        # Get database URL
        database_url = get_database_url()
        if not database_url:
            sys.exit(1)
        
        # Set up Alembic configuration
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        logger.info("Starting database migrations...")
        
        # Run migrations to head
        command.upgrade(alembic_cfg, "head")
        
        logger.info("✅ Database migrations completed successfully!")
        
        # Show current revision
        logger.info("Checking current database revision...")
        command.current(alembic_cfg, verbose=True)
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)


def check_migration_status():
    """Check the current migration status."""
    
    try:
        database_url = get_database_url()
        if not database_url:
            return
        
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        logger.info("Current migration status:")
        command.current(alembic_cfg, verbose=True)
        
        logger.info("\nAvailable migrations:")
        command.history(alembic_cfg, verbose=True)
        
    except Exception as e:
        logger.error(f"Failed to check migration status: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration runner")
    parser.add_argument("--check", action="store_true", help="Check migration status")
    parser.add_argument("--migrate", action="store_true", help="Run migrations")
    
    args = parser.parse_args()
    
    if args.check:
        check_migration_status()
    elif args.migrate:
        run_migrations()
    else:
        # Default action: run migrations
        run_migrations()