#!/usr/bin/env python
"""Railway startup script with migrations and graceful startup."""

import os
import sys
import uvicorn
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def run_migrations():
    """Run database migrations before starting the server."""
    try:
        print("📊 Running database migrations...")
        
        from alembic.config import Config
        from alembic import command
        
        # Get database URL
        database_url = os.getenv("DATABASE_URL") or os.getenv("DATABASE_PUBLIC_URL")
        if not database_url:
            print("⚠️  No DATABASE_URL found, skipping migrations")
            return True
        
        # Convert postgres:// to postgresql:// for SQLAlchemy
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        # Set up Alembic configuration
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        # Run migrations to head
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def main():
    """Main entry point for Railway deployment."""
    
    # Run migrations first
    if not run_migrations():
        print("❌ Failed to run migrations, exiting...")
        sys.exit(1)
    
    # Get port from Railway environment variable
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting Garmin AI Coach API on port {port}")
    
    # Start uvicorn server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
        reload=False,
        workers=1,
    )


if __name__ == "__main__":
    main()