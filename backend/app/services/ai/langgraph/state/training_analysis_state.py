"""Training Analysis State - Core state management for LangGraph workflow.

This replicates the exact state system from the CLI application to ensure
identical AI behavior and output generation.
"""

from typing import Dict, List, Optional, Any, Annotated
from typing_extensions import TypedDict
from datetime import datetime
from pydantic import BaseModel, Field
from langgraph.graph import add_messages
import operator


class ExpertOutput(BaseModel):
    """Structured output format for expert agents."""
    
    insights: str = Field(..., description="Main insights from analysis")
    patterns: List[str] = Field(default_factory=list, description="Key patterns identified")
    concerns: List[str] = Field(default_factory=list, description="Areas of concern")
    recommendations: List[str] = Field(default_factory=list, description="Specific recommendations")
    metrics_summary: Dict[str, Any] = Field(default_factory=dict, description="Key metrics summary")
    confidence_level: float = Field(default=0.8, description="Confidence in analysis (0-1)")
    additional_context: Optional[str] = Field(None, description="Additional context or notes")


class PlotReference(BaseModel):
    """Reference to a generated plot."""
    
    plot_id: str = Field(..., description="Unique plot identifier")
    plot_type: str = Field(..., description="Type of plot (line, bar, scatter, etc.)")
    title: str = Field(..., description="Plot title")
    description: str = Field(..., description="Plot description")
    data_source: str = Field(..., description="Source of plot data")
    file_path: Optional[str] = Field(None, description="Path to generated plot file")


class AnalysisProgress(BaseModel):
    """Progress tracking for analysis workflow."""
    
    current_step: str = Field(..., description="Current processing step")
    completed_steps: List[str] = Field(default_factory=list, description="Completed steps")
    total_steps: int = Field(default=9, description="Total number of steps")
    progress_percentage: float = Field(default=0.0, description="Progress as percentage")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    error_count: int = Field(default=0, description="Number of errors encountered")
    last_update: datetime = Field(default_factory=datetime.utcnow)


class TokenUsage(BaseModel):
    """Token usage tracking for cost management."""
    
    total_tokens: int = Field(default=0)
    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    estimated_cost: float = Field(default=0.0)
    model_used: Optional[str] = Field(None)
    provider: Optional[str] = Field(None)


class TrainingAnalysisState(TypedDict):
    """Central state management for training analysis workflow.
    
    This is the core state object that flows through all LangGraph nodes,
    exactly matching the CLI implementation structure.
    """
    
    # === CORE IDENTIFIERS ===
    analysis_id: str
    user_id: str
    training_config_id: str
    workflow_id: str
    
    # === ANALYSIS CONFIGURATION ===
    analysis_type: str  # "full_analysis", "quick_analysis", "planning_only"
    ai_mode: str  # "development", "standard", "cost_effective"
    enable_plotting: bool
    hitl_enabled: bool  # Human-in-the-Loop
    skip_synthesis: bool
    
    # === DATA EXTRACTION SETTINGS ===
    activities_days: int  # Number of days to extract activities
    metrics_days: int  # Number of days to extract metrics
    
    # === WORKFLOW CONTROL ===
    messages: Annotated[List[Dict[str, Any]], add_messages]
    current_step: str
    next_step: Optional[str]
    workflow_complete: bool
    
    # === PROGRESS TRACKING ===
    progress: AnalysisProgress
    start_time: datetime
    end_time: Optional[datetime]
    
    # === INPUT DATA ===
    user_profile: Optional[Dict[str, Any]]
    training_config: Optional[Dict[str, Any]]
    garmin_data: Optional[Dict[str, Any]]
    competition_schedule: Optional[List[Dict[str, Any]]]
    training_context: Optional[str]
    planning_context: Optional[str]
    
    # === RAW DATA SUMMARIES ===
    metrics_summary: Optional[str]
    physiology_summary: Optional[str]  
    activity_summary: Optional[str]
    
    # === EXPERT ANALYSIS OUTPUTS ===
    metrics_expert_output: Optional[ExpertOutput]
    physiology_expert_output: Optional[ExpertOutput]
    activity_expert_output: Optional[ExpertOutput]
    
    # === ORCHESTRATOR DECISIONS ===
    orchestrator_routing: Optional[str]  # "analysis", "planning", "both"
    orchestrator_reasoning: Optional[str]
    hitl_questions: Optional[List[str]]
    hitl_responses: Optional[Dict[str, str]]
    
    # === SYNTHESIS OUTPUT ===
    synthesis_output: Optional[str]
    formatted_analysis: Optional[str]
    
    # === PLANNING OUTPUTS ===
    season_plan: Optional[str]
    weekly_plan: Optional[str]
    plan_formatted: Optional[str]
    
    # === PLOT MANAGEMENT ===
    plot_references: List[PlotReference]
    plots_resolved: bool
    
    # === FINAL OUTPUTS ===
    final_analysis_html: Optional[str]
    final_planning_html: Optional[str]
    output_files: List[str]
    summary_json: Optional[Dict[str, Any]]
    
    # === ERROR HANDLING ===
    errors: List[str]
    warnings: List[str]
    retry_count: int
    
    # === COST TRACKING ===
    token_usage: Dict[str, TokenUsage]  # Keyed by agent/model
    total_cost: float
    
    # === METADATA ===
    created_at: datetime
    updated_at: datetime
    execution_metadata: Dict[str, Any]


def create_initial_state(
    analysis_id: str,
    user_id: str, 
    training_config_id: str,
    analysis_config: Dict[str, Any]
) -> TrainingAnalysisState:
    """Create initial state for training analysis workflow."""
    
    now = datetime.utcnow()
    
    return TrainingAnalysisState(
        # Core identifiers
        analysis_id=analysis_id,
        user_id=user_id,
        training_config_id=training_config_id,
        workflow_id=f"wf_{analysis_config.get('analysis_type', 'full')}_analysis_{now.strftime('%Y%m%d')}",
        
        # Configuration from request
        analysis_type=analysis_config.get("analysis_type", "full_analysis"),
        ai_mode=analysis_config.get("ai_mode", "development"),
        enable_plotting=analysis_config.get("enable_plotting", False),
        hitl_enabled=analysis_config.get("hitl_enabled", False),
        skip_synthesis=analysis_config.get("skip_synthesis", False),
        
        # Data extraction settings
        activities_days=analysis_config.get("activities_days", 21),
        metrics_days=analysis_config.get("metrics_days", 56),
        
        # Workflow control
        messages=[],
        current_step="data_extraction",
        next_step="parallel_summarization", 
        workflow_complete=False,
        
        # Progress tracking
        progress=AnalysisProgress(
            current_step="data_extraction",
            completed_steps=[],
            total_steps=9,
            progress_percentage=0.0,
            last_update=now
        ),
        start_time=now,
        end_time=None,
        
        # Initialize empty data structures
        user_profile=None,
        training_config=None,
        garmin_data=None,
        competition_schedule=None,
        training_context=None,
        planning_context=None,
        
        # Initialize summaries
        metrics_summary=None,
        physiology_summary=None,
        activity_summary=None,
        
        # Initialize expert outputs
        metrics_expert_output=None,
        physiology_expert_output=None,
        activity_expert_output=None,
        
        # Initialize orchestrator
        orchestrator_routing=None,
        orchestrator_reasoning=None,
        hitl_questions=None,
        hitl_responses=None,
        
        # Initialize outputs
        synthesis_output=None,
        formatted_analysis=None,
        season_plan=None,
        weekly_plan=None,
        plan_formatted=None,
        
        # Initialize plots
        plot_references=[],
        plots_resolved=False,
        
        # Initialize final outputs
        final_analysis_html=None,
        final_planning_html=None,
        output_files=[],
        summary_json=None,
        
        # Initialize error tracking
        errors=[],
        warnings=[],
        retry_count=0,
        
        # Initialize cost tracking
        token_usage={},
        total_cost=0.0,
        
        # Timestamps
        created_at=now,
        updated_at=now,
        execution_metadata={}
    )


def update_progress(state: TrainingAnalysisState, step: str, percentage: float) -> TrainingAnalysisState:
    """Update analysis progress."""
    
    now = datetime.utcnow()
    
    # Update progress
    if step not in state["progress"].completed_steps:
        state["progress"].completed_steps.append(step)
    
    state["progress"].current_step = step
    state["progress"].progress_percentage = percentage
    state["progress"].last_update = now
    
    # Update workflow state
    state["current_step"] = step
    state["updated_at"] = now
    
    return state


def add_token_usage(
    state: TrainingAnalysisState, 
    agent: str, 
    usage: TokenUsage
) -> TrainingAnalysisState:
    """Add token usage for cost tracking."""
    
    state["token_usage"][agent] = usage
    
    # Update total cost
    state["total_cost"] = sum(
        usage.estimated_cost for usage in state["token_usage"].values()
    )
    
    return state


def add_error(state: TrainingAnalysisState, error: str) -> TrainingAnalysisState:
    """Add error to state tracking."""
    
    state["errors"].append(error)
    state["progress"].error_count += 1
    state["updated_at"] = datetime.utcnow()
    
    return state


def add_plot_reference(state: TrainingAnalysisState, plot: PlotReference) -> TrainingAnalysisState:
    """Add plot reference for later resolution."""
    
    state["plot_references"].append(plot)
    state["updated_at"] = datetime.utcnow()
    
    return state