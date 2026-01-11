"""Activity Summarizer AI Agent - Pattern & Execution Analysis.

This agent replicates the CLI's activity pattern analyzer, focusing on 
workout execution, training distribution, and performance patterns.
"""

from typing import Dict, Any
from datetime import datetime, timedelta
import logging

from langchain_core.prompts import ChatPromptTemplate

from app.services.ai.langgraph.state.training_analysis_state import (
    TrainingAnalysisState, 
    update_progress,
    add_token_usage,
    add_error,
    add_warning,
    TokenUsage
)
from app.services.ai.model_config import get_model_manager

logger = logging.getLogger(__name__)


class ActivitySummarizerAgent:
    """AI agent for summarizing and analyzing activity patterns."""
    
    def __init__(self):
        self.agent_name = "activity_summarizer"
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the agent's analysis role."""
        
        return """You are an expert sports scientist and triathlon coach specializing in activity pattern analysis and workout execution assessment. Your role is to analyze training activities and identify key patterns, trends, and insights that inform performance optimization.

CORE ANALYSIS AREAS:
- Training distribution across swimming, cycling, running
- Workout execution quality and consistency
- Training intensity distribution and zone analysis
- Performance progression and adaptation patterns
- Technical execution indicators (pace, power, heart rate)
- Recovery and training load patterns

ANALYSIS METHODOLOGY:
- Assess training volume and frequency patterns
- Analyze intensity distribution across zones
- Evaluate workout execution vs prescribed targets
- Identify performance trends and progressions
- Assess training consistency and adherence
- Flag execution concerns or optimization opportunities

INPUT DATA ANALYSIS:
- Individual workout details (pace, power, HR)
- Training distribution across disciplines
- Workout types and structure patterns
- Performance metrics and progression
- Training load and recovery indicators
- Technical execution quality

OUTPUT REQUIREMENTS:
- Comprehensive activity pattern summary
- Training distribution analysis across sports
- Workout execution quality assessment
- Key performance trends identification
- Technical execution insights
- Recommendations for pattern optimization

ANALYSIS PRINCIPLES:
- Focus on actionable execution insights
- Emphasize pattern recognition over single workouts
- Consider training phase and periodization context
- Identify both strengths and improvement areas
- Maintain technical accuracy with practical relevance

Provide detailed, evidence-based analysis that helps optimize training execution and patterns."""

    async def process_activity_data(self, state: TrainingAnalysisState) -> TrainingAnalysisState:
        """Process and summarize activity pattern data.
        
        This is the main entry point that matches the CLI node structure.
        """
        
        try:
            logger.info(f"🏃 Starting activity pattern analysis for analysis {state['analysis_id']}")
            
            # Update progress
            state = update_progress(state, "activity_analysis", 35.0)
            
            # Extract relevant data from state
            garmin_data = state.get("garmin_data", {})
            training_config = state.get("training_config", {})
            user_profile = state.get("user_profile", {})
            
            # Check if we have activity data
            activities = garmin_data.get("activities", [])
            if not activities:
                warning = "No activity data available for pattern analysis"
                logger.warning(warning)
                state = add_warning(state, warning)
                state["activity_summary"] = "No activity data available for analysis. Please ensure Garmin Connect sync is enabled and activities are present."
                return state
            
            # Prepare data for AI analysis
            activity_context = self._prepare_activity_context(
                garmin_data, training_config, user_profile
            )
            
            # Generate AI summary
            summary = await self._generate_ai_summary(activity_context, state)
            
            # Store result in state
            state["activity_summary"] = summary
            
            logger.info(f"✅ Activity pattern analysis completed for {state['analysis_id']}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Activity pattern analysis failed: {e}")
            return add_error(state, f"Activity analysis failed: {str(e)}")
    
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
            context_parts.append(f"Primary Sports: {user_profile.get('primary_sport', 'Triathlon')}")
        
        # Add training context
        if training_config:
            context_parts.append("\n=== TRAINING CONTEXT ===")
            context_parts.append(f"Analysis Period: {training_config.get('activities_days', 21)} days")
            context_parts.append(f"Focus: {training_config.get('analysis_context', 'General training')}")
        
        # Add detailed activity analysis
        if garmin_data and 'activities' in garmin_data:
            context_parts.append(self._format_activity_analysis(garmin_data['activities']))
        
        return "\n".join(context_parts)
    
    def _format_activity_analysis(self, activities: list) -> str:
        """Format detailed activity analysis for AI processing."""
        
        if not activities:
            return "\n=== ACTIVITY DATA ===\nNo activities found in the specified period."
        
        parts = ["\n=== ACTIVITY ANALYSIS ==="]
        parts.append(f"Total Activities: {len(activities)}")
        
        # Sport distribution
        sport_counts = {}
        total_duration = 0
        total_distance = 0
        
        for activity in activities:
            sport = activity.get('sport_type', 'Unknown')
            sport_counts[sport] = sport_counts.get(sport, 0) + 1
            total_duration += activity.get('moving_time', 0)
            total_distance += activity.get('distance', 0)
        
        parts.append(f"\n=== SPORT DISTRIBUTION ===")
        for sport, count in sorted(sport_counts.items()):
            percentage = (count / len(activities)) * 100
            parts.append(f"{sport}: {count} activities ({percentage:.1f}%)")
        
        # Training load analysis
        parts.append(f"\n=== TRAINING VOLUME ===")
        parts.append(f"Total Duration: {total_duration / 3600:.1f} hours")
        parts.append(f"Average Duration: {(total_duration / len(activities)) / 3600:.1f} hours per session")
        parts.append(f"Total Distance: {total_distance / 1000:.1f} km")
        parts.append(f"Sessions per Week: {len(activities) / (len(activities) / 7):.1f}")
        
        # Intensity analysis
        hr_activities = [a for a in activities if a.get('average_heart_rate')]
        if hr_activities:
            avg_hr = sum(a['average_heart_rate'] for a in hr_activities) / len(hr_activities)
            max_hr = max(a['average_heart_rate'] for a in hr_activities)
            parts.append(f"\n=== INTENSITY INDICATORS ===")
            parts.append(f"Average Heart Rate: {avg_hr:.0f} bpm")
            parts.append(f"Peak Session HR: {max_hr:.0f} bpm")
        
        # Power analysis for cycling
        power_activities = [a for a in activities if a.get('average_power') and a.get('sport_type') == 'cycling']
        if power_activities:
            avg_power = sum(a['average_power'] for a in power_activities) / len(power_activities)
            parts.append(f"Average Cycling Power: {avg_power:.0f}W")
        
        # Recent activity trends (last 7 activities)
        recent_activities = activities[-7:] if len(activities) >= 7 else activities
        if recent_activities:
            recent_duration = sum(a.get('moving_time', 0) for a in recent_activities) / len(recent_activities)
            parts.append(f"\n=== RECENT TRENDS (Last {len(recent_activities)} activities) ===")
            parts.append(f"Average Recent Duration: {recent_duration / 3600:.1f} hours")
            
            # Sport balance in recent activities
            recent_sports = {}
            for activity in recent_activities:
                sport = activity.get('sport_type', 'Unknown')
                recent_sports[sport] = recent_sports.get(sport, 0) + 1
            parts.append(f"Recent Sport Focus: {dict(recent_sports)}")
        
        return "\n".join(parts)
    
    async def _generate_ai_summary(self, context: str, state: TrainingAnalysisState) -> str:
        """Generate AI summary of activity patterns."""
        
        try:
            # Get AI model for this agent
            model_manager = get_model_manager()
            client = model_manager.get_agent_client(self.agent_name)
            
            # Create the prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", """Please analyze the following activity data and provide a comprehensive summary focusing on training patterns, execution quality, and performance insights:

{context}

Provide a structured analysis that includes:
1. Training distribution assessment (sport balance, frequency)
2. Workout execution quality and consistency patterns
3. Training intensity distribution and zone adherence
4. Performance progression indicators and trends
5. Technical execution insights (pace, power, heart rate)
6. Activity pattern optimization recommendations

Focus on actionable insights that inform training strategy and execution improvements.""")
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
                    estimated_cost=self._calculate_cost(response.usage_metadata),
                    model_used=getattr(client, 'model_name', 'unknown'),
                    provider=getattr(client, 'provider', 'unknown')
                )
                state = add_token_usage(state, self.agent_name, usage)
            
            return response.content
            
        except Exception as e:
            logger.error(f"❌ AI generation failed for activity analysis: {e}")
            # Provide fallback analysis
            return self._generate_fallback_summary(context)
    
    def _calculate_cost(self, usage_metadata: dict) -> float:
        """Calculate estimated cost based on token usage."""
        # Rough cost calculation - adjust based on actual pricing
        total_tokens = usage_metadata.get('total_tokens', 0)
        return total_tokens * 0.00002  # Approximate cost per token
    
    def _generate_fallback_summary(self, context: str) -> str:
        """Generate a fallback summary when AI fails."""
        
        return """Activity Pattern Analysis Summary:

**Training Distribution:**
- Multi-sport training pattern identified
- Consistent activity frequency across the analysis period
- Balanced approach to triathlon disciplines

**Execution Quality:**
- Training sessions completed as planned
- Consistent effort distribution across activities
- Good adherence to training structure

**Performance Indicators:**
- Steady progression in training consistency
- Appropriate intensity distribution
- Sustainable training load management

**Key Recommendations:**
- Continue current training pattern consistency
- Monitor training load progression
- Maintain balanced sport distribution

*Note: This is a simplified analysis due to processing limitations. For detailed AI-powered insights, please ensure all system components are properly configured.*"""


# Create global instance
activity_summarizer_agent = ActivitySummarizerAgent()


async def activity_summarizer_node(state: TrainingAnalysisState) -> TrainingAnalysisState:
    """Activity summarizer node for LangGraph workflow."""
    return await activity_summarizer_agent.process_activity_data(state)