"""Garmin data models - exact replica of CLI data structures.

These models match the CLI's data extraction system to ensure
identical AI analysis behavior and output generation.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum


class ActivityType(str, Enum):
    """Garmin activity types."""
    
    RUNNING = "running"
    CYCLING = "cycling" 
    SWIMMING = "swimming"
    TRIATHLON = "triathlon"
    STRENGTH = "strength_training"
    OTHER = "other"


class IntensityLevel(str, Enum):
    """Training intensity levels."""
    
    RECOVERY = "recovery"
    EASY = "easy"
    MODERATE = "moderate"
    THRESHOLD = "threshold"
    VO2_MAX = "vo2_max"
    NEUROMUSCULAR = "neuromuscular"


class UserProfile(BaseModel):
    """Garmin user profile information."""
    
    user_id: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None
    last_login: Optional[datetime] = None


class DailyStats(BaseModel):
    """Daily statistics and metrics."""
    
    calendar_date: date
    steps: Optional[int] = None
    distance_meters: Optional[float] = None
    active_calories: Optional[int] = None
    bmr_calories: Optional[int] = None
    active_minutes: Optional[int] = None
    floors_climbed: Optional[int] = None
    min_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    resting_heart_rate: Optional[int] = None
    sleep_hours: Optional[float] = None
    deep_sleep_hours: Optional[float] = None
    rem_sleep_hours: Optional[float] = None
    awake_hours: Optional[float] = None


class ActivitySummary(BaseModel):
    """Activity summary data from Garmin."""
    
    activity_id: str
    activity_name: Optional[str] = None
    activity_type: ActivityType
    start_time: datetime
    duration_seconds: int
    distance_meters: Optional[float] = None
    calories: Optional[int] = None
    average_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    average_speed_mps: Optional[float] = None
    max_speed_mps: Optional[float] = None
    elevation_gain_meters: Optional[float] = None
    elevation_loss_meters: Optional[float] = None
    average_cadence: Optional[int] = None
    max_cadence: Optional[int] = None
    training_stress_score: Optional[float] = None
    intensity_factor: Optional[float] = None
    normalized_power: Optional[int] = None
    average_power: Optional[int] = None
    max_power: Optional[int] = None
    strokes: Optional[int] = None
    pool_length_meters: Optional[float] = None
    swolf_score: Optional[int] = None
    perceived_exertion: Optional[int] = None
    weather_temp_celsius: Optional[float] = None
    weather_condition: Optional[str] = None


class ActivityDetails(BaseModel):
    """Detailed activity data with time-series information."""
    
    activity_summary: ActivitySummary
    laps: List[Dict[str, Any]] = Field(default_factory=list)
    splits: List[Dict[str, Any]] = Field(default_factory=list)
    time_series_data: Dict[str, List[Any]] = Field(default_factory=dict)
    gear_used: Optional[Dict[str, str]] = None
    workout_type: Optional[str] = None
    training_effect: Optional[Dict[str, float]] = None


class PhysiologicalMarkers(BaseModel):
    """Physiological markers and recovery metrics."""
    
    measurement_date: date
    vo2_max: Optional[float] = None
    lactate_threshold_heart_rate: Optional[int] = None
    lactate_threshold_pace: Optional[float] = None
    functional_threshold_power: Optional[int] = None
    critical_swim_speed: Optional[float] = None
    body_battery: Optional[int] = None
    stress_level: Optional[int] = None
    recovery_time_hours: Optional[int] = None
    training_load_balance: Optional[str] = None
    acute_load: Optional[float] = None
    chronic_load: Optional[float] = None
    training_stress_balance: Optional[float] = None
    fitness_age: Optional[int] = None
    race_predictor_5k: Optional[str] = None
    race_predictor_10k: Optional[str] = None
    race_predictor_half_marathon: Optional[str] = None
    race_predictor_marathon: Optional[str] = None


class RecoveryIndicators(BaseModel):
    """Recovery and readiness indicators."""
    
    measurement_date: date
    hrv_rmssd: Optional[float] = None
    hrv_stress_score: Optional[int] = None
    recovery_advisor: Optional[str] = None
    training_readiness: Optional[int] = None
    sleep_score: Optional[int] = None
    stress_score: Optional[int] = None
    body_battery_charged: Optional[int] = None
    body_battery_drained: Optional[int] = None
    respiration_rate: Optional[float] = None
    spo2_average: Optional[float] = None
    spo2_lowest: Optional[float] = None


class TrainingStatus(BaseModel):
    """Training status and load information."""
    
    status_date: date
    training_status: Optional[str] = None  # "peaking", "productive", "maintaining", etc.
    load_ratio: Optional[float] = None
    acute_load: Optional[float] = None
    chronic_load: Optional[float] = None
    load_focus: Optional[str] = None
    training_effect_aerobic: Optional[float] = None
    training_effect_anaerobic: Optional[float] = None
    total_training_effect: Optional[float] = None
    recovery_time: Optional[int] = None
    recovery_heart_rate: Optional[int] = None


class BodyMetrics(BaseModel):
    """Body composition and health metrics."""
    
    measurement_date: date
    weight_kg: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    skeletal_muscle_mass_kg: Optional[float] = None
    bone_mass_kg: Optional[float] = None
    body_water_percentage: Optional[float] = None
    metabolic_age: Optional[int] = None
    visceral_fat_rating: Optional[int] = None
    bmi: Optional[float] = None


class HeartRateZones(BaseModel):
    """Heart rate zone definitions and time in zones."""
    
    zone_date: date
    max_heart_rate: Optional[int] = None
    lactate_threshold_heart_rate: Optional[int] = None
    
    # Zone boundaries
    zone_1_min: Optional[int] = None
    zone_1_max: Optional[int] = None
    zone_2_min: Optional[int] = None
    zone_2_max: Optional[int] = None
    zone_3_min: Optional[int] = None
    zone_3_max: Optional[int] = None
    zone_4_min: Optional[int] = None
    zone_4_max: Optional[int] = None
    zone_5_min: Optional[int] = None
    zone_5_max: Optional[int] = None
    
    # Time in zones (minutes)
    time_in_zone_1: Optional[int] = None
    time_in_zone_2: Optional[int] = None
    time_in_zone_3: Optional[int] = None
    time_in_zone_4: Optional[int] = None
    time_in_zone_5: Optional[int] = None


class GarminData(BaseModel):
    """Complete Garmin Connect data structure.
    
    This is the main data structure that contains all extracted
    information from Garmin Connect for AI analysis.
    """
    
    # User information
    user_profile: Optional[UserProfile] = None
    
    # Time-series data
    daily_stats: List[DailyStats] = Field(default_factory=list)
    activities: List[ActivitySummary] = Field(default_factory=list)
    activity_summaries: List[ActivitySummary] = Field(default_factory=list)
    
    # Physiological data
    physiological_markers: List[PhysiologicalMarkers] = Field(default_factory=list)
    recovery_indicators: List[RecoveryIndicators] = Field(default_factory=list)
    training_status: List[TrainingStatus] = Field(default_factory=list)
    
    # Body composition
    body_metrics: List[BodyMetrics] = Field(default_factory=list)
    heart_rate_zones: List[HeartRateZones] = Field(default_factory=list)
    
    # Data extraction metadata
    extraction_date: datetime = Field(default_factory=datetime.utcnow)
    activities_days: int = 21
    metrics_days: int = 56
    total_activities: int = 0
    total_distance_km: float = 0.0
    total_duration_hours: float = 0.0
    
    # Data quality indicators
    data_completeness_score: float = 0.0
    has_heart_rate_data: bool = False
    has_power_data: bool = False
    has_pace_data: bool = False
    has_recovery_data: bool = False
    
    # Summary statistics
    avg_weekly_distance_km: Optional[float] = None
    avg_weekly_duration_hours: Optional[float] = None
    avg_weekly_activities: Optional[float] = None
    activity_type_distribution: Dict[str, int] = Field(default_factory=dict)
    intensity_distribution: Dict[str, float] = Field(default_factory=dict)
    
    def calculate_summary_stats(self) -> None:
        """Calculate summary statistics from the raw data."""
        
        if not self.activities:
            return
        
        # Calculate totals
        self.total_activities = len(self.activities)
        self.total_distance_km = sum(
            (a.distance_meters or 0) / 1000 for a in self.activities
        )
        self.total_duration_hours = sum(
            a.duration_seconds / 3600 for a in self.activities
        )
        
        # Calculate averages (assuming data covers requested days)
        weeks = max(self.activities_days / 7, 1)
        self.avg_weekly_distance_km = self.total_distance_km / weeks
        self.avg_weekly_duration_hours = self.total_duration_hours / weeks
        self.avg_weekly_activities = self.total_activities / weeks
        
        # Activity type distribution
        self.activity_type_distribution = {}
        for activity in self.activities:
            activity_type = activity.activity_type
            self.activity_type_distribution[activity_type] = (
                self.activity_type_distribution.get(activity_type, 0) + 1
            )
        
        # Data quality assessment
        hr_activities = sum(1 for a in self.activities if a.average_heart_rate)
        power_activities = sum(1 for a in self.activities if a.average_power)
        pace_activities = sum(1 for a in self.activities if a.average_speed_mps)
        
        self.has_heart_rate_data = hr_activities > 0
        self.has_power_data = power_activities > 0 
        self.has_pace_data = pace_activities > 0
        self.has_recovery_data = len(self.recovery_indicators) > 0
        
        # Completeness score (0-1)
        total_possible_data_points = len(self.activities) * 4  # HR, power, pace, recovery
        actual_data_points = hr_activities + power_activities + pace_activities + (
            len(self.recovery_indicators) if self.has_recovery_data else 0
        )
        
        self.data_completeness_score = (
            actual_data_points / total_possible_data_points if total_possible_data_points > 0 else 0
        )
    
    def get_activity_summary_text(self) -> str:
        """Generate a text summary of the activity data for AI processing."""
        
        if not self.activities:
            return "No activity data available for analysis."
        
        summary_parts = [
            f"Data Period: {self.activities_days} days of activities, {self.metrics_days} days of metrics",
            f"Total Activities: {self.total_activities}",
            f"Total Distance: {self.total_distance_km:.1f} km",
            f"Total Duration: {self.total_duration_hours:.1f} hours",
            f"Weekly Averages: {self.avg_weekly_activities:.1f} activities, {self.avg_weekly_distance_km:.1f} km, {self.avg_weekly_duration_hours:.1f} hours"
        ]
        
        if self.activity_type_distribution:
            type_summary = ", ".join([
                f"{activity_type}: {count}" 
                for activity_type, count in self.activity_type_distribution.items()
            ])
            summary_parts.append(f"Activity Types: {type_summary}")
        
        data_availability = []
        if self.has_heart_rate_data:
            data_availability.append("Heart Rate")
        if self.has_power_data:
            data_availability.append("Power")
        if self.has_pace_data:
            data_availability.append("Pace")
        if self.has_recovery_data:
            data_availability.append("Recovery Metrics")
        
        if data_availability:
            summary_parts.append(f"Available Data Types: {', '.join(data_availability)}")
        
        summary_parts.append(f"Data Completeness: {self.data_completeness_score:.1%}")
        
        return "\n".join(summary_parts)