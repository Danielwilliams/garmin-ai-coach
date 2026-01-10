"""Pydantic schemas for analysis API."""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from uuid import UUID


class AnalysisResultCreate(BaseModel):
    """Schema for creating an analysis result."""
    node_name: str = Field(..., min_length=1, max_length=100)
    result_type: str = Field(..., pattern="^(summary|plan|plot|recommendation|data)$")
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = Field(None, max_length=500)
    tokens_used: int = Field(0, ge=0)
    processing_time: Optional[int] = Field(None, ge=0)


class AnalysisResultResponse(AnalysisResultCreate):
    """Schema for analysis result response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    analysis_id: UUID
    created_at: datetime
    updated_at: datetime


class AnalysisFileCreate(BaseModel):
    """Schema for creating an analysis file."""
    filename: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(..., pattern="^(plot|report|data|export)$")
    mime_type: str = Field(..., max_length=100)
    file_size: int = Field(..., ge=0)
    file_path: str = Field(..., max_length=500)
    is_public: bool = Field(False)


class AnalysisFileResponse(AnalysisFileCreate):
    """Schema for analysis file response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    analysis_id: UUID
    download_count: int
    created_at: datetime
    updated_at: datetime


class AnalysisCreate(BaseModel):
    """Schema for creating an analysis."""
    training_config_id: UUID
    analysis_type: str = Field("full_analysis", max_length=50)
    workflow_id: Optional[str] = Field(None, max_length=100)


class AnalysisUpdate(BaseModel):
    """Schema for updating an analysis."""
    status: Optional[str] = Field(None, pattern="^(pending|running|completed|failed|cancelled)$")
    current_node: Optional[str] = Field(None, max_length=100)
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    summary: Optional[str] = None
    recommendations: Optional[str] = None
    weekly_plan: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    data_summary: Optional[Dict[str, Any]] = None
    total_tokens: Optional[int] = Field(None, ge=0)
    estimated_cost: Optional[str] = Field(None, max_length=20)
    error_message: Optional[str] = None
    retry_count: Optional[int] = Field(None, ge=0)


class AnalysisResponse(BaseModel):
    """Schema for analysis response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    training_config_id: UUID
    status: str
    analysis_type: str
    workflow_id: Optional[str]
    current_node: Optional[str]
    progress_percentage: int
    summary: Optional[str]
    recommendations: Optional[str]
    weekly_plan: Optional[Dict[str, Any]]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    data_summary: Optional[Dict[str, Any]]
    total_tokens: int
    estimated_cost: Optional[str]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: datetime


class AnalysisWithResults(AnalysisResponse):
    """Schema for analysis with results and files."""
    results: List[AnalysisResultResponse] = Field(default_factory=list)
    files: List[AnalysisFileResponse] = Field(default_factory=list)
    training_config_name: Optional[str] = None


class AnalysisSummary(BaseModel):
    """Schema for analysis summary in list view."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    status: str
    analysis_type: str
    progress_percentage: int
    training_config_name: str
    total_tokens: int
    estimated_cost: Optional[str]
    created_at: datetime
    has_summary: bool = False
    has_recommendations: bool = False
    has_weekly_plan: bool = False
    files_count: int = 0
    results_count: int = 0


class AnalysisStatsResponse(BaseModel):
    """Schema for analysis statistics."""
    total_analyses: int
    completed_analyses: int
    running_analyses: int
    failed_analyses: int
    total_tokens_used: int
    total_cost_usd: float
    avg_processing_time_minutes: float