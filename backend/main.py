"""FastAPI application entry point."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="Garmin AI Coach API",
    description="AI-powered triathlon coaching platform with Garmin Connect integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Garmin AI Coach API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "status": "running",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "port": os.getenv("PORT", "8000")
    }

# Test endpoint
@app.get("/test")
async def test():
    return {"message": "Backend is working correctly!", "success": True}