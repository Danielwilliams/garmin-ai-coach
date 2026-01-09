"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Database initialization removed - tables managed externally
from app.api.auth import router as auth_router


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
    lifespan=lifespan
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

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Garmin AI Coach API",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "status": "running",
        "features": ["authentication", "multi-tenant", "database"],
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