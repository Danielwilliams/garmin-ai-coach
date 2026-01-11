"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Database initialization removed - tables managed externally
from app.api.auth import router as auth_router
from app.api.training_profiles import router as training_profiles_router

# Import analyses router with error handling and fallback
try:
    from app.api.analyses import router as analyses_router
    ANALYSES_AVAILABLE = True
    print("✅ Full analyses router imported successfully")
except ImportError as e:
    print(f"❌ Failed to import full analyses router: {e}")
    print("🔄 Falling back to minimal analyses router...")
    try:
        from app.api.analyses_minimal import router as analyses_router
        ANALYSES_AVAILABLE = True
        print("✅ Minimal analyses router imported successfully")
    except ImportError as e2:
        print(f"❌ Failed to import minimal analyses router: {e2}")
        ANALYSES_AVAILABLE = False
        analyses_router = None

from app.api.mock_data import router as mock_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting Garmin AI Coach API...")
    print("✅ Database tables assumed to exist (managed externally)")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Garmin AI Coach API",
    description="AI-powered triathlon coaching platform with Garmin Connect integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    redirect_slashes=False
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(training_profiles_router, prefix="/api/v1")

# Include analyses router only if available
if ANALYSES_AVAILABLE and analyses_router is not None:
    app.include_router(analyses_router, prefix="/api/v1")
    print("✅ Analyses router registered")
else:
    print("❌ Analyses router not available - skipping registration")

app.include_router(mock_router, prefix="/api/v1")  # For testing dashboard

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Garmin AI Coach API",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "status": "running",
        "features": ["authentication", "training-profiles", "analysis", "multi-tenant", "database"],
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Test endpoint
@app.get("/test")
async def test():
    return {"message": "Phase 2: Multi-tenancy ready!", "success": True}