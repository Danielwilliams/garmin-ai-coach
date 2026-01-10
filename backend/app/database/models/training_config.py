"""Training configuration models (web version of YAML config)."""

from sqlalchemy import Column, String, Boolean, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base


class TrainingConfig(Base):
    """User's training configuration (replaces YAML config)."""
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Foreign key to User
    name = Column(String(100), nullable=False)  # Config name (e.g., "Spring Training 2024")
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Analysis context (from YAML)
    analysis_context = Column(Text, nullable=True)
    planning_context = Column(Text, nullable=True)
    
    # Data extraction settings
    activities_days = Column(Integer, default=21, nullable=False)
    metrics_days = Column(Integer, default=56, nullable=False)
    ai_mode = Column(String(20), default="standard", nullable=False)  # development, standard, cost_effective
    enable_plotting = Column(Boolean, default=False, nullable=False)
    hitl_enabled = Column(Boolean, default=True, nullable=False)  # Human-in-the-loop
    skip_synthesis = Column(Boolean, default=False, nullable=False)
    
    # Output settings
    output_directory = Column(String(255), default="./data", nullable=False)
    
    # Relationships
    # user = relationship("User", back_populates="training_configs")
    # competitions = relationship("Competition", back_populates="training_config")


class Competition(Base):
    """Competition/race information."""
    
    training_config_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Foreign key
    
    name = Column(String(200), nullable=False)
    date = Column(String(20), nullable=False)  # YYYY-MM-DD or text format
    race_type = Column(String(50), nullable=False)  # Olympic, Sprint, etc.
    priority = Column(String(1), nullable=False)  # A, B, C
    target_time = Column(String(10), nullable=True)  # HH:MM:SS format
    
    # External race data
    bikereg_id = Column(Integer, nullable=True)
    runreg_url = Column(String(500), nullable=True)
    
    # Relationships
    # training_config = relationship("TrainingConfig", back_populates="competitions")


class TrainingZone(Base):
    """Training zones for different disciplines."""
    
    training_config_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Foreign key
    
    discipline = Column(String(20), nullable=False)  # Running, Cycling, Swimming
    metric = Column(String(100), nullable=False)  # Description like "LTHR ≈ 171 bpm / 4:35 min/km"
    value = Column(String(50), nullable=False)  # Value like "171 bpm", "213W", "1:30/100m"
    
    # Relationships (commented until we set up proper relationships)
    # training_config = relationship("TrainingConfig", back_populates="training_zones")