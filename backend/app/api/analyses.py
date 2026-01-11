"""Analysis API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, case
from uuid import UUID

from app.database.base import get_db
from app.database.models.user import User
from app.database.models.training_config import TrainingConfig
from app.database.models.analysis import Analysis, AnalysisResult, AnalysisFile
from app.schemas.analysis import (
    AnalysisCreate,
    AnalysisUpdate,
    AnalysisResponse,
    AnalysisWithResults,
    AnalysisSummary,
    AnalysisStatsResponse,
    AnalysisResultCreate,
    AnalysisResultResponse,
    AnalysisFileCreate,
    AnalysisFileResponse
)
from app.dependencies import get_current_user
import os
from pathlib import Path
from fastapi.responses import FileResponse

# Import report generator with error handling for missing dependencies
try:
    from app.services.report_generator import report_generator
    REPORT_GENERATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Report generator not available - {e}")
    REPORT_GENERATOR_AVAILABLE = False
    report_generator = None

# Import AI analysis engine with fallback
try:
    from app.services.ai.analysis_engine import AnalysisEngine
    analysis_engine = AnalysisEngine()
    AI_ENGINE_AVAILABLE = True
    print("✅ AI analysis engine loaded successfully")
except ImportError as e:
    print(f"Warning: AI engine not available - {e}")
    AI_ENGINE_AVAILABLE = False
    analysis_engine = None
except Exception as e:
    print(f"Warning: AI engine initialization failed - {e}")
    AI_ENGINE_AVAILABLE = False
    analysis_engine = None

router = APIRouter(prefix="/analyses", tags=["analyses"])

# Debug endpoint
@router.get("/debug")
async def debug_endpoint():
    """Debug endpoint to test if route registration is working."""
    return {"status": "analyses router is working", "message": "Debug endpoint active"}


@router.get("/", response_model=List[AnalysisSummary])
async def list_analyses(
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    training_config_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get list of user's analyses with summary info."""
    
    # Base query with joins for summary data
    query = select(
        Analysis.id,
        Analysis.status,
        Analysis.analysis_type,
        Analysis.progress_percentage,
        Analysis.total_tokens,
        Analysis.estimated_cost,
        Analysis.created_at,
        TrainingConfig.name.label('training_config_name'),
        # Check if analysis has content
        case((Analysis.summary.isnot(None), True), else_=False).label('has_summary'),
        case((Analysis.recommendations.isnot(None), True), else_=False).label('has_recommendations'),
        case((Analysis.weekly_plan.isnot(None), True), else_=False).label('has_weekly_plan'),
        # Count related records
        func.count(AnalysisFile.id).label('files_count'),
        func.count(AnalysisResult.id).label('results_count')
    ).select_from(
        Analysis
    ).join(
        TrainingConfig, TrainingConfig.id == Analysis.training_config_id
    ).outerjoin(
        AnalysisFile, AnalysisFile.analysis_id == Analysis.id
    ).outerjoin(
        AnalysisResult, AnalysisResult.analysis_id == Analysis.id
    ).where(
        Analysis.user_id == current_user.id
    ).group_by(
        Analysis.id, TrainingConfig.name
    ).order_by(
        desc(Analysis.created_at)
    )
    
    # Apply filters
    if status:
        query = query.where(Analysis.status == status)
    
    if training_config_id:
        query = query.where(Analysis.training_config_id == training_config_id)
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    analyses = result.all()
    
    return [
        AnalysisSummary(
            id=analysis.id,
            status=analysis.status,
            analysis_type=analysis.analysis_type,
            progress_percentage=analysis.progress_percentage,
            training_config_name=analysis.training_config_name,
            total_tokens=analysis.total_tokens,
            estimated_cost=analysis.estimated_cost,
            created_at=analysis.created_at,
            has_summary=analysis.has_summary,
            has_recommendations=analysis.has_recommendations,
            has_weekly_plan=analysis.has_weekly_plan,
            files_count=analysis.files_count or 0,
            results_count=analysis.results_count or 0
        )
        for analysis in analyses
    ]


@router.get("/{analysis_id}", response_model=AnalysisWithResults)
async def get_analysis(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed analysis with results and files."""
    
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
    
    # Get training config name
    config_query = select(TrainingConfig.name).where(
        TrainingConfig.id == analysis.training_config_id
    )
    config_result = await db.execute(config_query)
    training_config_name = config_result.scalar_one_or_none()
    
    # Get analysis results
    results_query = select(AnalysisResult).where(
        AnalysisResult.analysis_id == analysis_id
    ).order_by(AnalysisResult.created_at)
    results_result = await db.execute(results_query)
    results = results_result.scalars().all()
    
    # Get analysis files
    files_query = select(AnalysisFile).where(
        AnalysisFile.analysis_id == analysis_id
    ).order_by(AnalysisFile.created_at)
    files_result = await db.execute(files_query)
    files = files_result.scalars().all()
    
    # Create response
    analysis_dict = {
        "id": analysis.id,
        "user_id": analysis.user_id,
        "training_config_id": analysis.training_config_id,
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
        "training_config_name": training_config_name,
        "results": [
            {
                "id": result.id,
                "analysis_id": result.analysis_id,
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
        "files": [
            {
                "id": file.id,
                "analysis_id": file.analysis_id,
                "filename": file.filename,
                "file_type": file.file_type,
                "mime_type": file.mime_type,
                "file_size": file.file_size,
                "file_path": file.file_path,
                "is_public": file.is_public,
                "download_count": file.download_count,
                "created_at": file.created_at,
                "updated_at": file.updated_at,
            }
            for file in files
        ]
    }
    
    return AnalysisWithResults.model_validate(analysis_dict)


@router.post("/", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    analysis_data: AnalysisCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new analysis using the AI engine.
    
    Note: This endpoint is deprecated. Use POST /training-profiles/{id}/start-analysis instead.
    """
    
    # Verify the training config belongs to the user
    config_query = select(TrainingConfig).where(
        and_(
            TrainingConfig.id == analysis_data.training_config_id,
            TrainingConfig.user_id == current_user.id
        )
    )
    config_result = await db.execute(config_query)
    training_config = config_result.scalar_one_or_none()
    
    if not training_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training config not found"
        )
    
    # Check if AI engine is available
    if not AI_ENGINE_AVAILABLE:
        # Fallback to simple analysis creation
        analysis = Analysis(
            user_id=current_user.id,
            training_config_id=analysis_data.training_config_id,
            analysis_type=analysis_data.analysis_type,
            workflow_id=analysis_data.workflow_id,
            status="pending",
            progress_percentage=0,
            total_tokens=0,
            retry_count=0
        )
        
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        
        return AnalysisResponse.model_validate(analysis)
    
    # Use AI engine to start analysis
    try:
        # Prepare analysis configuration from training config and request
        analysis_config = {
            "analysis_type": analysis_data.analysis_type,
            "ai_mode": training_config.ai_mode,
            "activities_days": training_config.activities_days,
            "metrics_days": training_config.metrics_days,
            "enable_plotting": training_config.enable_plotting,
            "hitl_enabled": training_config.hitl_enabled,
            "skip_synthesis": training_config.skip_synthesis,
            "workflow_id": analysis_data.workflow_id
        }
        
        # Start analysis using AI engine
        analysis_id = await analysis_engine.start_analysis(
            user_id=str(current_user.id),
            training_config_id=str(analysis_data.training_config_id),
            analysis_config=analysis_config,
            db=db
        )
        
        # Create analysis record in database
        analysis = Analysis(
            id=UUID(analysis_id),
            user_id=current_user.id,
            training_config_id=analysis_data.training_config_id,
            analysis_type=analysis_data.analysis_type,
            workflow_id=analysis_data.workflow_id,
            status="running",
            progress_percentage=0,
            total_tokens=0,
            retry_count=0
        )
        
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        
        return AnalysisResponse.model_validate(analysis)
        
    except Exception as e:
        # If AI engine fails, create analysis in failed state
        analysis = Analysis(
            user_id=current_user.id,
            training_config_id=analysis_data.training_config_id,
            analysis_type=analysis_data.analysis_type,
            workflow_id=analysis_data.workflow_id,
            status="failed",
            error_message=f"Failed to start AI analysis: {str(e)}",
            progress_percentage=0,
            total_tokens=0,
            retry_count=0
        )
        
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        
        return AnalysisResponse.model_validate(analysis)


@router.put("/{analysis_id}", response_model=AnalysisResponse)
async def update_analysis(
    analysis_id: UUID,
    analysis_update: AnalysisUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an analysis."""
    
    # Get the analysis
    query = select(Analysis).where(
        and_(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Update fields
    update_data = analysis_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(analysis, field, value)
    
    await db.commit()
    await db.refresh(analysis)
    
    return AnalysisResponse.model_validate(analysis)


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an analysis."""
    
    query = select(Analysis).where(
        and_(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    await db.delete(analysis)
    await db.commit()


@router.get("/{analysis_id}/results", response_model=List[AnalysisResultResponse])
async def get_analysis_results(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    result_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get results for a specific analysis."""
    
    # Verify analysis ownership
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
    
    # Get results
    query = select(AnalysisResult).where(AnalysisResult.analysis_id == analysis_id)
    
    if result_type:
        query = query.where(AnalysisResult.result_type == result_type)
    
    query = query.order_by(AnalysisResult.created_at)
    
    result = await db.execute(query)
    results = result.scalars().all()
    
    return [AnalysisResultResponse.model_validate(r) for r in results]


@router.post("/{analysis_id}/results", response_model=AnalysisResultResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis_result(
    analysis_id: UUID,
    result_data: AnalysisResultCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new analysis result."""
    
    # Verify analysis ownership
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
    
    # Create the result
    result = AnalysisResult(
        analysis_id=analysis_id,
        node_name=result_data.node_name,
        result_type=result_data.result_type,
        title=result_data.title,
        content=result_data.content,
        data=result_data.data,
        file_path=result_data.file_path,
        tokens_used=result_data.tokens_used,
        processing_time=result_data.processing_time
    )
    
    db.add(result)
    await db.commit()
    await db.refresh(result)
    
    return AnalysisResultResponse.model_validate(result)


@router.get("/{analysis_id}/files", response_model=List[AnalysisFileResponse])
async def get_analysis_files(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    file_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get files for a specific analysis."""
    
    # Verify analysis ownership
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
    
    # Get files
    query = select(AnalysisFile).where(AnalysisFile.analysis_id == analysis_id)
    
    if file_type:
        query = query.where(AnalysisFile.file_type == file_type)
    
    query = query.order_by(AnalysisFile.created_at)
    
    result = await db.execute(query)
    files = result.scalars().all()
    
    return [AnalysisFileResponse.model_validate(f) for f in files]


@router.get("/stats/summary", response_model=AnalysisStatsResponse)
async def get_analysis_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analysis statistics for the user."""
    
    # Get analysis counts by status
    stats_query = select(
        func.count(Analysis.id).label('total_analyses'),
        func.sum(case((Analysis.status == 'completed', 1), else_=0)).label('completed_analyses'),
        func.sum(case((Analysis.status == 'running', 1), else_=0)).label('running_analyses'),
        func.sum(case((Analysis.status == 'failed', 1), else_=0)).label('failed_analyses'),
        func.sum(Analysis.total_tokens).label('total_tokens_used'),
        func.avg(
            case(
                (and_(Analysis.start_date.isnot(None), Analysis.end_date.isnot(None)),
                 func.extract('epoch', Analysis.end_date - Analysis.start_date) / 60.0),
                else_=None
            )
        ).label('avg_processing_time_minutes')
    ).where(
        Analysis.user_id == current_user.id
    )
    
    result = await db.execute(stats_query)
    stats = result.first()
    
    # Calculate total cost (simplified - would need actual pricing logic)
    total_cost_usd = (stats.total_tokens_used or 0) * 0.0001  # Example: $0.0001 per token
    
    return AnalysisStatsResponse(
        total_analyses=stats.total_analyses or 0,
        completed_analyses=stats.completed_analyses or 0,
        running_analyses=stats.running_analyses or 0,
        failed_analyses=stats.failed_analyses or 0,
        total_tokens_used=stats.total_tokens_used or 0,
        total_cost_usd=total_cost_usd,
        avg_processing_time_minutes=stats.avg_processing_time_minutes or 0.0
    )


@router.post("/{analysis_id}/generate-report")
async def generate_analysis_report(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate an HTML report for the analysis."""
    
    if not REPORT_GENERATOR_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Report generation service is not available. Please contact support."
        )
    
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
    
    # Get training config name
    config_query = select(TrainingConfig.name).where(
        TrainingConfig.id == analysis.training_config_id
    )
    config_result = await db.execute(config_query)
    training_config_name = config_result.scalar_one_or_none()
    
    # Get analysis results
    results_query = select(AnalysisResult).where(
        AnalysisResult.analysis_id == analysis_id
    ).order_by(AnalysisResult.created_at)
    results_result = await db.execute(results_query)
    results = results_result.scalars().all()
    
    # Convert to dict format for report generator
    analysis_data = {
        "id": str(analysis.id),
        "analysis_type": analysis.analysis_type,
        "status": analysis.status,
        "progress_percentage": analysis.progress_percentage,
        "summary": analysis.summary,
        "recommendations": analysis.recommendations,
        "weekly_plan": analysis.weekly_plan,
        "total_tokens": analysis.total_tokens,
        "estimated_cost": analysis.estimated_cost,
        "created_at": analysis.created_at,
        "training_config_name": training_config_name
    }
    
    results_data = [
        {
            "node_name": result.node_name,
            "result_type": result.result_type,
            "title": result.title,
            "content": result.content,
            "data": result.data,
            "tokens_used": result.tokens_used,
            "processing_time": result.processing_time
        }
        for result in results
    ]
    
    # Generate report
    try:
        report_info = report_generator.generate_analysis_report(
            analysis_data=analysis_data,
            results_data=results_data,
            user_name=current_user.full_name or current_user.email
        )
        
        # Save file reference to database
        analysis_file = AnalysisFile(
            analysis_id=analysis_id,
            filename=report_info["filename"],
            file_type="report",
            mime_type=report_info["mime_type"],
            file_size=report_info["file_size"],
            file_path=report_info["file_path"],
            is_public=False,
            download_count=0
        )
        
        db.add(analysis_file)
        await db.commit()
        await db.refresh(analysis_file)
        
        return {
            "status": "success",
            "message": "Report generated successfully",
            "report": report_info,
            "download_url": f"/api/v1/analyses/files/{report_info['filename']}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.post("/{analysis_id}/export-data")
async def export_analysis_data(
    analysis_id: UUID,
    export_format: str = "json",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export analysis data in JSON or CSV format."""
    
    if not REPORT_GENERATOR_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Export service is not available. Please contact support."
        )
    
    if export_format not in ["json", "csv"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Export format must be 'json' or 'csv'"
        )
    
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
    
    # Convert to dict format for report generator
    analysis_data = {
        "id": str(analysis.id),
        "analysis_type": analysis.analysis_type,
        "status": analysis.status,
        "created_at": analysis.created_at,
        "total_tokens": analysis.total_tokens,
        "estimated_cost": analysis.estimated_cost,
        "summary": analysis.summary,
        "recommendations": analysis.recommendations,
        "weekly_plan": analysis.weekly_plan,
        "data_summary": analysis.data_summary
    }
    
    results_data = [
        {
            "node_name": result.node_name,
            "result_type": result.result_type,
            "title": result.title,
            "content": result.content,
            "data": result.data,
            "tokens_used": result.tokens_used
        }
        for result in results
    ]
    
    # Generate export
    try:
        export_info = report_generator.generate_data_export(
            analysis_data=analysis_data,
            results_data=results_data,
            export_format=export_format
        )
        
        # Save file reference to database
        analysis_file = AnalysisFile(
            analysis_id=analysis_id,
            filename=export_info["filename"],
            file_type="export",
            mime_type=export_info["mime_type"],
            file_size=export_info["file_size"],
            file_path=export_info["file_path"],
            is_public=False,
            download_count=0
        )
        
        db.add(analysis_file)
        await db.commit()
        await db.refresh(analysis_file)
        
        return {
            "status": "success",
            "message": f"Data exported successfully as {export_format.upper()}",
            "export": export_info,
            "download_url": f"/api/v1/analyses/files/{export_info['filename']}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export data: {str(e)}"
        )


@router.post("/{analysis_id}/export-weekly-plan")
async def export_weekly_plan(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export weekly training plan as CSV."""
    
    if not REPORT_GENERATOR_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Export service is not available. Please contact support."
        )
    
    # Get the analysis
    analysis_query = select(Analysis.weekly_plan, Analysis.id).where(
        and_(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id
        )
    )
    analysis_result = await db.execute(analysis_query)
    analysis_data = analysis_result.first()
    
    if not analysis_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    if not analysis_data.weekly_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No weekly plan available for this analysis"
        )
    
    # Get full analysis for metadata
    full_analysis_query = select(Analysis).where(Analysis.id == analysis_id)
    full_analysis_result = await db.execute(full_analysis_query)
    full_analysis = full_analysis_result.scalar_one()
    
    # Generate export
    try:
        export_info = report_generator.generate_weekly_plan_export(
            weekly_plan_data=analysis_data.weekly_plan,
            analysis_data={
                "id": str(full_analysis.id),
                "analysis_type": full_analysis.analysis_type,
                "created_at": full_analysis.created_at
            }
        )
        
        # Save file reference to database
        analysis_file = AnalysisFile(
            analysis_id=analysis_id,
            filename=export_info["filename"],
            file_type="weekly_plan",
            mime_type=export_info["mime_type"],
            file_size=export_info["file_size"],
            file_path=export_info["file_path"],
            is_public=False,
            download_count=0
        )
        
        db.add(analysis_file)
        await db.commit()
        await db.refresh(analysis_file)
        
        return {
            "status": "success",
            "message": "Weekly plan exported successfully",
            "export": export_info,
            "download_url": f"/api/v1/analyses/files/{export_info['filename']}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export weekly plan: {str(e)}"
        )


@router.get("/files/{file_path:path}")
async def serve_file(file_path: str):
    """Serve generated files for download."""
    
    # Security: Only allow files from our designated directories
    allowed_dirs = [
        Path(os.getenv("REPORTS_OUTPUT_DIR", "./storage/reports")),
        Path(os.getenv("EXPORTS_OUTPUT_DIR", "./storage/exports")),
        Path(os.getenv("PLOTS_OUTPUT_DIR", "./storage/plots"))
    ]
    
    # Resolve the full path
    full_path = None
    for allowed_dir in allowed_dirs:
        potential_path = allowed_dir / file_path
        if potential_path.exists() and potential_path.is_file():
            # Additional security check: ensure the file is within the allowed directory
            try:
                potential_path.resolve().relative_to(allowed_dir.resolve())
                full_path = potential_path
                break
            except ValueError:
                # Path is outside the allowed directory
                continue
    
    if not full_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Determine media type
    media_type = "application/octet-stream"
    if full_path.suffix == ".html":
        media_type = "text/html"
    elif full_path.suffix == ".json":
        media_type = "application/json"
    elif full_path.suffix == ".csv":
        media_type = "text/csv"
    elif full_path.suffix in [".png", ".jpg", ".jpeg"]:
        media_type = f"image/{full_path.suffix[1:]}"
    
    return FileResponse(
        path=full_path,
        media_type=media_type,
        filename=full_path.name
    )