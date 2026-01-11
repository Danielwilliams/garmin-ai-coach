"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
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
    print("❌ Analyses router not available - adding fallback routes")
    
    # Add minimal fallback routes directly to main app
    from app.database.base import get_db
    from app.dependencies import get_current_user
    from app.database.models.user import User
    from sqlalchemy.ext.asyncio import AsyncSession
    
    @app.get("/api/v1/analyses")
    async def fallback_list_analyses(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        """Fallback analyses list endpoint."""
        try:
            from app.database.models.analysis import Analysis
            from sqlalchemy import select, desc
            
            query = select(Analysis).where(
                Analysis.user_id == current_user.id
            ).order_by(desc(Analysis.created_at)).limit(50)
            
            result = await db.execute(query)
            analyses = result.scalars().all()
            
            return [
                {
                    "id": str(analysis.id),
                    "status": analysis.status,
                    "analysis_type": analysis.analysis_type,
                    "progress_percentage": analysis.progress_percentage,
                    "training_config_name": "Unknown",
                    "total_tokens": analysis.total_tokens,
                    "estimated_cost": analysis.estimated_cost,
                    "created_at": analysis.created_at,
                    "has_summary": bool(analysis.summary),
                    "has_recommendations": bool(analysis.recommendations),
                    "has_weekly_plan": bool(analysis.weekly_plan),
                    "files_count": 0,
                    "results_count": 0
                }
                for analysis in analyses
            ]
        except Exception as e:
            print(f"❌ Fallback analyses list failed: {e}")
            return []
    
    @app.get("/api/v1/analyses/{analysis_id}")
    async def fallback_get_analysis(
        analysis_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        """Fallback individual analysis endpoint."""
        try:
            from app.database.models.analysis import Analysis, AnalysisResult
            from sqlalchemy import select, and_
            from uuid import UUID
            
            # Get the analysis
            analysis_query = select(Analysis).where(
                and_(
                    Analysis.id == UUID(analysis_id),
                    Analysis.user_id == current_user.id
                )
            )
            analysis_result = await db.execute(analysis_query)
            analysis = analysis_result.scalar_one_or_none()
            
            if not analysis:
                raise HTTPException(status_code=404, detail="Analysis not found")
            
            # Get analysis results
            results_query = select(AnalysisResult).where(
                AnalysisResult.analysis_id == UUID(analysis_id)
            ).order_by(AnalysisResult.created_at)
            results_result = await db.execute(results_query)
            results = results_result.scalars().all()
            
            return {
                "id": str(analysis.id),
                "user_id": str(analysis.user_id),
                "training_config_id": str(analysis.training_config_id),
                "status": analysis.status,
                "analysis_type": analysis.analysis_type,
                "workflow_id": analysis.workflow_id,
                "current_node": analysis.current_node,
                "progress_percentage": analysis.progress_percentage,
                "summary": analysis.summary,
                "recommendations": analysis.recommendations,
                "weekly_plan": analysis.weekly_plan,
                "start_date": analysis.start_date,
                "end_date": analysis.end_date,
                "data_summary": analysis.data_summary,
                "total_tokens": analysis.total_tokens,
                "estimated_cost": analysis.estimated_cost,
                "error_message": analysis.error_message,
                "retry_count": analysis.retry_count,
                "created_at": analysis.created_at,
                "updated_at": analysis.updated_at,
                "training_config_name": "Unknown",
                "results": [
                    {
                        "id": str(result.id),
                        "analysis_id": str(result.analysis_id),
                        "node_name": result.node_name,
                        "result_type": result.result_type,
                        "title": result.title,
                        "content": result.content,
                        "data": result.data,
                        "file_path": result.file_path,
                        "tokens_used": result.tokens_used,
                        "processing_time": result.processing_time,
                        "created_at": result.created_at,
                        "updated_at": result.updated_at,
                    }
                    for result in results
                ],
                "files": []
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Fallback get analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get analysis: {str(e)}")

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

# Debug routes endpoint
@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to show all registered routes."""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": getattr(route, 'name', 'unknown')
            })
    return {"routes": routes}