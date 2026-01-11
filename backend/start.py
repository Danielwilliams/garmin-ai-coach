#!/usr/bin/env python
"""Railway startup script with health checks and graceful shutdown."""

import os
import uvicorn

def main():
    """Main entry point for Railway deployment."""
    
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