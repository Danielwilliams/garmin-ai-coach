#!/usr/bin/env python
"""Railway startup script with health checks and graceful shutdown."""

import asyncio
import logging
import os
import signal
import sys
from contextlib import asynccontextmanager

import uvicorn

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)


class GracefulShutdown:
    """Handle graceful shutdown of the application."""
    
    def __init__(self):
        self.shutdown = False
        self.server = None
    
    def exit_gracefully(self, signum, frame):
        """Signal handler for graceful shutdown."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown = True
        
        if self.server:
            self.server.should_exit = True


async def startup_tasks():
    """Perform startup tasks."""
    logger.info("Starting Railway deployment...")
    logger.info("Startup tasks completed")


async def shutdown_tasks():
    """Perform shutdown tasks."""
    logger.info("Performing shutdown tasks...")
    logger.info("Shutdown tasks completed")


def main():
    """Main entry point for Railway deployment."""
    
    # Setup graceful shutdown
    shutdown_handler = GracefulShutdown()
    signal.signal(signal.SIGINT, shutdown_handler.exit_gracefully)
    signal.signal(signal.SIGTERM, shutdown_handler.exit_gracefully)
    
    # Configuration for Railway
    config = uvicorn.Config(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info",
        access_log=True,
        reload=False,  # Never reload on Railway
        workers=1,  # Single worker for Railway (they handle scaling)
    )
    
    server = uvicorn.Server(config)
    shutdown_handler.server = server
    
    # Run startup tasks
    asyncio.run(startup_tasks())
    
    try:
        # Start the server
        logger.info(f"Starting server on port {config.port}")
        server.run()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        # Run shutdown tasks
        asyncio.run(shutdown_tasks())
        logger.info("Application stopped")


if __name__ == "__main__":
    main()