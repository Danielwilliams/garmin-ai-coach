"""Activity Summarizer AI Agent - Workout Execution & Activity Pattern Analysis.

This agent replicates the CLI's activity summarizer with the same
AI prompts, processing logic, and output format.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from app.services.ai.langgraph.state.training_analysis_state import (
    TrainingAnalysisState, 
    update_progress,
    add_token_usage,
    add_error,
    TokenUsage
)
from app.services.ai.model_config import get_model_manager

logger = logging.getLogger(__name__)


class ActivitySummarizerAgent:
    """AI agent for summarizing activity data and workout execution patterns."""
    
    def __init__(self):
        self.agent_name = "activity_summarizer"
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the agent's role and expertise."""
        
        return """You are an AI expert specializing in workout analysis and activity pattern recognition for triathlon athletes. Your role is to analyze and summarize training activities with a focus on:

CORE EXPERTISE:
- Workout execution and quality analysis
- Training pattern recognition and consistency
- Activity distribution and periodization
- Performance trends across disciplines
- Workout intensity and effort analysis
- Training load distribution patterns

ANALYSIS FOCUS:
- Workout execution quality vs planned intentions
- Training consistency and adherence patterns
- Activity type distribution and balance
- Intensity distribution across workouts
- Performance progression indicators
- Seasonal and weekly training patterns
- Recovery workout identification and analysis

INPUT DATA TYPES:
- Individual activity summaries with metrics
- Workout duration, distance, and intensity data
- Heart rate, power, and pace information
- Training stress scores and perceived exertion
- Activity types and training zones
- Seasonal activity patterns and trends

OUTPUT REQUIREMENTS:
- Concise summary of activity patterns and trends
- Assessment of workout execution quality
- Analysis of training distribution and balance
- Identification of performance progression
- Training consistency and adherence insights
- Notable workout performances and outliers
- Activity pattern recommendations

ANALYSIS PRINCIPLES:
- Focus on execution quality over raw numbers
- Emphasize training pattern consistency
- Consider seasonal and weekly periodization
- Identify both strengths and improvement areas
- Relate activity patterns to training goals
- Balance detail with actionable insights
- Consider recovery and adaptation patterns

Be thorough but concise. Focus on activity patterns and execution quality that will inform training decisions and program adjustments."""

    async def process_activity_data(self, state: TrainingAnalysisState) -> TrainingAnalysisState:
        """Process and summarize activity and workout execution data."""
        
        try:
            logger.info(f"🏃 Starting activity summarization for analysis {state['analysis_id']}")
            
            # Update progress
            state = update_progress(state, "activity_summarization", 15.0)
            
            # Extract relevant data from state
            garmin_data = state.get("garmin_data", {})
            training_config = state.get("training_config", {})
            user_profile = state.get("user_profile", {})
            
            # Prepare data for AI analysis
            activity_context = self._prepare_activity_context(
                garmin_data, training_config, user_profile
            )
            
            # Generate AI summary
            summary = await self._generate_ai_summary(activity_context, state)
            
            # Store result in state
            state["activity_summary"] = summary
            
            logger.info(f"✅ Activity summarization completed for {state['analysis_id']}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Activity summarization failed: {e}")
            return add_error(state, f"Activity summarization failed: {str(e)}")
    
    def _prepare_activity_context(
        self, 
        garmin_data: Dict[str, Any],
        training_config: Dict[str, Any], 
        user_profile: Dict[str, Any]
    ) -> str:
        """Prepare activity context for AI analysis."""
        
        context_parts = []
        
        # Add athlete context
        context_parts.append("=== ATHLETE PROFILE ===")
        if user_profile:
            context_parts.append(f"Athlete: {user_profile.get('display_name', 'Unknown')}")
            if user_profile.get('birth_date'):
                context_parts.append(f"Age: {self._calculate_age(user_profile['birth_date'])}")
            context_parts.append(f"Weight: {user_profile.get('weight_kg', 'Unknown')} kg")
        
        # Add training context
        if training_config:
            context_parts.append("\n=== TRAINING CONTEXT ===")
            context_parts.append(f"Analysis Period: {training_config.get('activities_days', 21)} days")
            context_parts.append(f"Training Focus: {training_config.get('analysis_context', 'General training')}")
        
        # Add activity overview
        if garmin_data and 'activities' in garmin_data:
            context_parts.append(self._format_activity_overview(garmin_data['activities']))
        
        # Add detailed activity analysis
        if garmin_data and 'activities' in garmin_data:
            context_parts.append(self._format_activity_patterns(garmin_data['activities']))
        
        # Add workout execution analysis
        if garmin_data and 'activities' in garmin_data:
            context_parts.append(self._format_workout_execution(garmin_data['activities']))
        
        # Add performance trends
        if garmin_data and 'activities' in garmin_data:
            context_parts.append(self._format_performance_trends(garmin_data['activities']))
        
        return "\n".join(context_parts)
    
    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date."""
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except:
            return 0
    
    def _format_activity_overview(self, activities: list) -> str:
        """Format activity overview for analysis."""
        
        if not activities:
            return "\n=== ACTIVITY OVERVIEW ===\nNo activity data available"
        
        parts = ["\n=== ACTIVITY OVERVIEW ==="]
        
        # Basic statistics
        total_activities = len(activities)
        total_duration = sum(a.get('duration_seconds', 0) for a in activities) / 3600  # hours
        total_distance = sum(a.get('distance_meters', 0) for a in activities) / 1000  # km
        
        parts.append(f"Total Activities: {total_activities}")
        parts.append(f"Total Duration: {total_duration:.1f} hours")
        parts.append(f"Total Distance: {total_distance:.1f} km")
        
        # Activity type distribution
        type_counts = {}
        for activity in activities:
            activity_type = activity.get('activity_type', 'unknown')
            type_counts[activity_type] = type_counts.get(activity_type, 0) + 1
        
        if type_counts:
            type_summary = ", ".join([f"{type_name}: {count}" for type_name, count in type_counts.items()])
            parts.append(f"Activity Types: {type_summary}")
        
        # Weekly averages
        weeks = max(len(activities) / 7, 1)
        avg_weekly_activities = total_activities / weeks
        avg_weekly_duration = total_duration / weeks
        avg_weekly_distance = total_distance / weeks
        
        parts.append(f"Weekly Averages: {avg_weekly_activities:.1f} activities, {avg_weekly_duration:.1f}h, {avg_weekly_distance:.1f}km")
        
        return "\n".join(parts)
    
    def _format_activity_patterns(self, activities: list) -> str:
        """Format activity pattern analysis."""
        
        if not activities:
            return ""
        
        parts = ["\n=== ACTIVITY PATTERNS ==="]
        
        # Analyze by day of week
        day_patterns = {}
        for activity in activities:
            day_of_week = activity.get('start_time', datetime.now()).weekday()
            day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day_of_week]
            day_patterns[day_name] = day_patterns.get(day_name, 0) + 1
        
        if day_patterns:
            day_summary = ", ".join([f"{day}: {count}" for day, count in sorted(day_patterns.items())])
            parts.append(f"Weekly Pattern: {day_summary}")
        
        # Training load distribution
        tss_values = [a.get('training_stress_score', 0) for a in activities if a.get('training_stress_score')]
        if tss_values:
            avg_tss = sum(tss_values) / len(tss_values)
            min_tss = min(tss_values)
            max_tss = max(tss_values)
            parts.append(f"Training Load (TSS): Avg {avg_tss:.0f}, Range {min_tss:.0f}-{max_tss:.0f}")
        
        # Duration distribution
        durations = [a.get('duration_seconds', 0) / 60 for a in activities]  # minutes
        if durations:
            avg_duration = sum(durations) / len(durations)
            short_workouts = len([d for d in durations if d < 30])
            medium_workouts = len([d for d in durations if 30 <= d <= 90])
            long_workouts = len([d for d in durations if d > 90])
            parts.append(f"Duration Distribution: Short (<30min): {short_workouts}, Medium (30-90min): {medium_workouts}, Long (>90min): {long_workouts}")
        
        return "\n".join(parts)
    
    def _format_workout_execution(self, activities: list) -> str:
        """Format workout execution quality analysis."""
        
        if not activities:
            return ""
        
        parts = ["\n=== WORKOUT EXECUTION ANALYSIS ==="]
        
        # Heart rate analysis
        hr_activities = [a for a in activities if a.get('average_heart_rate')]
        if hr_activities:
            avg_hr = sum(a['average_heart_rate'] for a in hr_activities) / len(hr_activities)
            parts.append(f"Average Heart Rate: {avg_hr:.0f} bpm ({len(hr_activities)} activities with HR data)")
        
        # Power analysis (if available)
        power_activities = [a for a in activities if a.get('average_power')]
        if power_activities:
            avg_power = sum(a['average_power'] for a in power_activities) / len(power_activities)
            parts.append(f"Average Power: {avg_power:.0f}W ({len(power_activities)} activities with power data)")
        
        # Pace/speed analysis
        pace_activities = [a for a in activities if a.get('average_speed_mps')]
        if pace_activities:
            avg_speed = sum(a['average_speed_mps'] for a in pace_activities) / len(pace_activities)
            # Convert to min/km for running-like activities
            if avg_speed > 0:
                pace_min_km = (1000 / avg_speed) / 60
                parts.append(f"Average Pace: {pace_min_km:.2f} min/km ({avg_speed:.1f} m/s)")
        
        # Perceived exertion analysis
        rpe_activities = [a for a in activities if a.get('perceived_exertion')]
        if rpe_activities:
            avg_rpe = sum(a['perceived_exertion'] for a in rpe_activities) / len(rpe_activities)
            easy_workouts = len([a for a in rpe_activities if a['perceived_exertion'] <= 3])
            moderate_workouts = len([a for a in rpe_activities if 4 <= a['perceived_exertion'] <= 6])
            hard_workouts = len([a for a in rpe_activities if a['perceived_exertion'] >= 7])
            parts.append(f"Perceived Exertion: Avg {avg_rpe:.1f} (Easy: {easy_workouts}, Moderate: {moderate_workouts}, Hard: {hard_workouts})")
        
        return "\n".join(parts)
    
    def _format_performance_trends(self, activities: list) -> str:
        """Format performance trend analysis."""
        
        if len(activities) < 5:
            return "\n=== PERFORMANCE TRENDS ===\nInsufficient data for trend analysis"
        
        parts = ["\n=== PERFORMANCE TRENDS ==="]
        
        # Sort activities by date
        sorted_activities = sorted(activities, key=lambda x: x.get('start_time', datetime.min))
        
        # Analyze recent vs early performance
        early_activities = sorted_activities[:len(sorted_activities)//3]
        recent_activities = sorted_activities[-len(sorted_activities)//3:]
        
        # TSS trend
        early_tss = [a.get('training_stress_score', 0) for a in early_activities if a.get('training_stress_score')]
        recent_tss = [a.get('training_stress_score', 0) for a in recent_activities if a.get('training_stress_score')]
        
        if early_tss and recent_tss:
            early_avg_tss = sum(early_tss) / len(early_tss)
            recent_avg_tss = sum(recent_tss) / len(recent_tss)
            tss_change = ((recent_avg_tss - early_avg_tss) / early_avg_tss) * 100 if early_avg_tss > 0 else 0
            trend_direction = "increasing" if tss_change > 5 else "decreasing" if tss_change < -5 else "stable"
            parts.append(f"Training Load Trend: {trend_direction} ({tss_change:+.1f}% change)")
        
        # Heart rate trend
        early_hr = [a.get('average_heart_rate', 0) for a in early_activities if a.get('average_heart_rate')]
        recent_hr = [a.get('average_heart_rate', 0) for a in recent_activities if a.get('average_heart_rate')]
        
        if early_hr and recent_hr:
            early_avg_hr = sum(early_hr) / len(early_hr)
            recent_avg_hr = sum(recent_hr) / len(recent_hr)
            hr_change = recent_avg_hr - early_avg_hr
            parts.append(f"Heart Rate Trend: {recent_avg_hr:.0f} bpm (recent) vs {early_avg_hr:.0f} bpm (early), change: {hr_change:+.0f} bpm")
        
        # Speed/pace trend
        early_speed = [a.get('average_speed_mps', 0) for a in early_activities if a.get('average_speed_mps')]
        recent_speed = [a.get('average_speed_mps', 0) for a in recent_activities if a.get('average_speed_mps')]
        
        if early_speed and recent_speed:
            early_avg_speed = sum(early_speed) / len(early_speed)
            recent_avg_speed = sum(recent_speed) / len(recent_speed)
            speed_change = ((recent_avg_speed - early_avg_speed) / early_avg_speed) * 100 if early_avg_speed > 0 else 0
            trend_direction = "improving" if speed_change > 2 else "declining" if speed_change < -2 else "stable"
            parts.append(f"Speed Trend: {trend_direction} ({speed_change:+.1f}% change)")
        
        # Activity frequency trend
        early_weeks = len(set([a.get('start_time', datetime.min).isocalendar()[1] for a in early_activities]))
        recent_weeks = len(set([a.get('start_time', datetime.min).isocalendar()[1] for a in recent_activities]))
        
        if early_weeks > 0 and recent_weeks > 0:
            early_freq = len(early_activities) / early_weeks
            recent_freq = len(recent_activities) / recent_weeks
            freq_change = recent_freq - early_freq
            parts.append(f"Training Frequency: {recent_freq:.1f} activities/week (recent) vs {early_freq:.1f} activities/week (early), change: {freq_change:+.1f}")
        
        return "\n".join(parts)
    
    async def _generate_ai_summary(self, context: str, state: TrainingAnalysisState) -> str:
        """Generate AI summary of activity data."""
        
        try:
            # Get AI model for this agent
            model_manager = get_model_manager()
            client = model_manager.get_agent_client(self.agent_name)
            
            # Create the prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", """Please analyze the following activity data and provide a comprehensive summary focusing on workout execution quality, activity patterns, and performance trends:

{context}

Provide a structured summary that includes:
1. Activity pattern analysis (volume, frequency, distribution)
2. Workout execution quality assessment
3. Training consistency and adherence patterns
4. Performance progression indicators and trends
5. Notable workouts, outliers, or concerns
6. Activity balance across training disciplines

Focus on execution quality, training patterns, and progression indicators that inform coaching decisions and training program adjustments.""")
            ])
            
            # Generate response
            messages = prompt.format_messages(context=context)
            response = await client.ainvoke(messages)
            
            # Extract and track token usage
            if hasattr(response, 'usage_metadata'):
                usage = TokenUsage(
                    total_tokens=response.usage_metadata.get('total_tokens', 0),
                    prompt_tokens=response.usage_metadata.get('input_tokens', 0),
                    completion_tokens=response.usage_metadata.get('output_tokens', 0),
                    model_used=model_manager.get_model_for_agent(self.agent_name).model_id,
                    provider=model_manager.get_model_for_agent(self.agent_name).provider.value
                )
                usage.estimated_cost = model_manager.estimate_cost(self.agent_name, usage.total_tokens)
                
                state = add_token_usage(state, self.agent_name, usage)
            
            summary = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"🏃 Generated activity summary: {len(summary)} characters")
            return summary
            
        except Exception as e:
            logger.error(f"❌ AI summary generation failed: {e}")
            raise


# Node function for LangGraph integration
async def activity_summarizer_node(state: TrainingAnalysisState) -> TrainingAnalysisState:
    """LangGraph node function for activity summarization."""
    
    agent = ActivitySummarizerAgent()
    return await agent.process_activity_data(state)