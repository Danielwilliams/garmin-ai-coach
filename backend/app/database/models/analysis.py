"""Analysis and AI coaching result models."""

from sqlalchemy import Column, String, Text, JSON, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base


class Analysis(Base):
    """AI coaching analysis session."""
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Foreign key to User
    training_config_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Foreign key
    
    # Analysis metadata
    status = Column(String(20), default="pending", nullable=False)  # pending, running, completed, failed
    analysis_type = Column(String(50), nullable=False)  # full_analysis, planning_only, etc.
    
    # LangGraph workflow tracking
    workflow_id = Column(String(100), nullable=True)
    current_node = Column(String(100), nullable=True)
    progress_percentage = Column(Integer, default=0, nullable=False)
    
    # Results
    summary = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    weekly_plan = Column(JSON, nullable=True)  # Structured weekly plan
    
    # Analysis context
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    data_summary = Column(JSON, nullable=True)  # Activities/metrics summary
    
    # Cost tracking
    total_tokens = Column(Integer, default=0, nullable=False)
    estimated_cost = Column(String(20), nullable=True)  # "$0.15" format
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    # user = relationship("User", back_populates="analyses")
    # training_config = relationship("TrainingConfig")
    # results = relationship("AnalysisResult", back_populates="analysis")


class AnalysisResult(Base):
    """Individual result components from analysis."""
    
    analysis_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Foreign key
    
    # Result metadata
    node_name = Column(String(100), nullable=False)  # Which LangGraph node generated this
    result_type = Column(String(50), nullable=False)  # summary, plan, plot, recommendation
    title = Column(String(200), nullable=False)
    
    # Content
    content = Column(Text, nullable=True)  # Text content
    data = Column(JSON, nullable=True)  # Structured data
    file_path = Column(String(500), nullable=True)  # Path to generated files (plots, etc.)
    
    # Processing metadata
    tokens_used = Column(Integer, default=0, nullable=False)
    processing_time = Column(Integer, nullable=True)  # Seconds
    
    # Relationships
    # analysis = relationship("Analysis", back_populates="results")


class AnalysisFile(Base):
    """Files generated during analysis (plots, reports, etc.)."""
    
    analysis_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Foreign key
    
    # File metadata
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # plot, report, data
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)  # Bytes
    
    # Storage
    file_path = Column(String(500), nullable=False)  # Local/S3 path
    is_public = Column(Boolean, default=False, nullable=False)
    download_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    # analysis = relationship("Analysis")