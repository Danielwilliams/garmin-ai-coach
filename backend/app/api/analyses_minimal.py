"""Minimal Analysis API endpoints for debugging and basic functionality."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from uuid import UUID

from app.database.base import get_db
from app.database.models.user import User
from app.database.models.analysis import Analysis, AnalysisResult
from app.dependencies import get_current_user

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.get("/debug")
async def debug_minimal():
    """Debug endpoint for minimal analyses router."""
    return {"status": "minimal analyses router working", "message": "Basic functionality active"}


@router.get("/")
async def list_analyses_minimal(
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get list of user's analyses - minimal version."""
    
    try:
        # Simple query without complex joins
        query = select(Analysis).where(
            Analysis.user_id == current_user.id
        ).order_by(
            desc(Analysis.created_at)
        ).offset(offset).limit(limit)
        
        result = await db.execute(query)
        analyses = result.scalars().all()
        
        # Return simplified response
        return [
            {
                "id": str(analysis.id),
                "status": analysis.status,
                "analysis_type": analysis.analysis_type,
                "progress_percentage": analysis.progress_percentage,
                "training_config_name": "Unknown",  # Simplified for now
                "total_tokens": analysis.total_tokens,
                "estimated_cost": analysis.estimated_cost,
                "created_at": analysis.created_at,
                "has_summary": bool(analysis.summary),
                "has_recommendations": bool(analysis.recommendations),
                "has_weekly_plan": bool(analysis.weekly_plan),
                "files_count": 0,  # Simplified
                "results_count": 0  # Simplified
            }
            for analysis in analyses
        ]
        
    except Exception as e:
        print(f"❌ Error in list_analyses_minimal: {e}")
        return []


@router.get("/{analysis_id}")
async def get_analysis_minimal(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed analysis - minimal version."""
    
    try:
        # Get the analysis
        analysis_query = select(Analysis).where(
            and_(
                Analysis.id == analysis_id,
                Analysis.user_id == current_user.id
            )
        )
        analysis_result = await db.execute(analysis_query)
        analysis = analysis_result.scalar_one_or_none()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        # Get analysis results
        results_query = select(AnalysisResult).where(
            AnalysisResult.analysis_id == analysis_id
        ).order_by(AnalysisResult.created_at)
        results_result = await db.execute(results_query)
        results = results_result.scalars().all()
        
        # Return simplified response
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
            "training_config_name": "Unknown",  # Simplified
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
            "files": []  # Simplified for now
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_analysis_minimal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis: {str(e)}"
        )