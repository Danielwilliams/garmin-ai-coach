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

router = APIRouter(prefix="/analyses", tags=["analyses"])


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
    """Create a new analysis."""
    
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
    
    # Create the analysis
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