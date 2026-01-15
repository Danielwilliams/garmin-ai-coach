"""Pydantic schemas for training profile API."""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class TrainingZoneCreate(BaseModel):
    """Schema for creating a training zone."""
    discipline: str = Field(..., description="Training discipline: Running, Cycling, or Swimming")
    metric: str = Field(..., min_length=1, max_length=100, description="Zone description")
    value: str = Field(..., min_length=1, max_length=50, description="Zone value")


class TrainingZoneResponse(TrainingZoneCreate):
    """Schema for training zone response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    training_config_id: UUID
    created_at: datetime
    updated_at: datetime


class CompetitionCreate(BaseModel):
    """Schema for creating a competition."""
    name: str = Field(..., min_length=1, max_length=200, description="Competition name")
    date: str = Field(..., min_length=1, max_length=20, description="Competition date")
    race_type: str = Field(..., min_length=1, max_length=50, description="Race type")
    priority: str = Field(..., pattern="^[ABC]$", description="Priority: A, B, or C")
    target_time: Optional[str] = Field(None, max_length=10, description="Target time in HH:MM:SS")
    bikereg_id: Optional[int] = Field(None, description="BikeReg event ID")
    runreg_url: Optional[str] = Field(None, max_length=500, description="RunReg event URL")


class CompetitionResponse(CompetitionCreate):
    """Schema for competition response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    training_config_id: UUID
    created_at: datetime
    updated_at: datetime


class TrainingConfigCreate(BaseModel):
    """Schema for creating a training configuration."""
    name: str = Field(..., min_length=1, max_length=100, description="Configuration name")
    analysis_context: str = Field(..., min_length=10, description="Analysis context")
    planning_context: str = Field(..., min_length=10, description="Planning context")
    
    # Data extraction settings
    activities_days: int = Field(21, ge=1, le=365, description="Days of activity data")
    metrics_days: int = Field(56, ge=1, le=365, description="Days of metrics data")
    ai_mode: str = Field("standard", pattern="^(development|standard|cost_effective)$")
    enable_plotting: bool = Field(False, description="Enable analysis plotting")
    hitl_enabled: bool = Field(True, description="Human-in-the-loop enabled")
    skip_synthesis: bool = Field(False, description="Skip synthesis step")
    
    # Output settings
    output_directory: str = Field("./data", min_length=1, description="Output directory")
    
    # Training zones and competitions
    training_zones: List[TrainingZoneCreate] = Field(default_factory=list)
    competitions: List[CompetitionCreate] = Field(default_factory=list)


class TrainingConfigUpdate(BaseModel):
    """Schema for updating a training configuration."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    analysis_context: Optional[str] = Field(None, min_length=10)
    planning_context: Optional[str] = Field(None, min_length=10)
    activities_days: Optional[int] = Field(None, ge=1, le=365)
    metrics_days: Optional[int] = Field(None, ge=1, le=365)
    ai_mode: Optional[str] = Field(None, pattern="^(development|standard|cost_effective)$")
    enable_plotting: Optional[bool] = None
    hitl_enabled: Optional[bool] = None
    skip_synthesis: Optional[bool] = None
    output_directory: Optional[str] = Field(None, min_length=1)
    is_active: Optional[bool] = None


class TrainingConfigResponse(BaseModel):
    """Schema for training configuration response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    is_active: bool

    # Athlete information
    athlete_name: Optional[str] = None
    athlete_email: Optional[str] = None

    # Context
    analysis_context: Optional[str]
    planning_context: Optional[str]
    training_needs: Optional[str] = None
    session_constraints: Optional[str] = None
    training_preferences: Optional[str] = None

    # Settings
    activities_days: int
    metrics_days: int
    ai_mode: str
    enable_plotting: bool
    hitl_enabled: bool
    skip_synthesis: bool
    output_directory: str

    # Garmin Connect credentials (email only, password is encrypted)
    garmin_email: Optional[str] = None
    garmin_is_connected: bool = False
    garmin_last_sync: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Related data (loaded separately)
    training_zones: List[TrainingZoneResponse] = Field(default_factory=list)
    competitions: List[CompetitionResponse] = Field(default_factory=list)


class TrainingProfileSummary(BaseModel):
    """Schema for training profile list view."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    is_active: bool
    athlete_name: Optional[str] = None
    competitions_count: int = 0
    zones_count: int = 0
    ai_mode: str

    # Garmin connection status
    garmin_email: Optional[str] = None
    garmin_is_connected: bool = False
    garmin_last_sync: Optional[str] = None

    created_at: datetime
    updated_at: datetime


class GarminCredentialsUpdate(BaseModel):
    """Schema for updating Garmin credentials."""
    email: str = Field(..., description="Garmin Connect email")
    password: str = Field(..., min_length=6, description="Garmin Connect password")


class GarminAccountResponse(BaseModel):
    """Schema for Garmin account response (without password)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    email: str
    is_connected: bool
    last_sync: Optional[datetime]
    sync_error: Optional[str]
    activities_days: str
    metrics_days: str
    created_at: datetime
    updated_at: datetime


# Frontend form data schema that maps to our backend models
class TrainingProfileFormData(BaseModel):
    """Schema for frontend training profile wizard form data."""
    
    # Step 1: Athlete Information (goes to User table)
    athlete_name: str = Field(..., min_length=2, max_length=100)
    athlete_email: str = Field(..., description="Email address")
    
    # Step 2: Training Context
    analysis_context: str = Field(..., min_length=10)
    planning_context: str = Field(..., min_length=10)
    training_needs: Optional[str] = None
    session_constraints: Optional[str] = None
    training_preferences: Optional[str] = None
    
    # Step 3: Training Zones
    zones: List[TrainingZoneCreate] = Field(..., min_items=1)
    
    # Step 4: Competitions
    competitions: List[CompetitionCreate] = Field(..., min_items=1)
    
    # Step 5: External Races (optional)
    bikereg_events: List[CompetitionCreate] = Field(default_factory=list)
    runreg_events: List[CompetitionCreate] = Field(default_factory=list)
    
    # Step 6: Analysis Settings
    activities_days: int = Field(21, ge=1, le=365)
    metrics_days: int = Field(56, ge=1, le=365)
    ai_mode: str = Field("standard", pattern="^(development|standard|cost_effective)$")
    enable_plotting: bool = Field(False)
    hitl_enabled: bool = Field(True)
    skip_synthesis: bool = Field(False)
    
    # Step 7: Output & Garmin Settings
    output_directory: str = Field("./data", min_length=1)
    garmin_email: str = Field(..., description="Garmin Connect email")
    garmin_password: str = Field(..., min_length=6, description="Garmin Connect password")