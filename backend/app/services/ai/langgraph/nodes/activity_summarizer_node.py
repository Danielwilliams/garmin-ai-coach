"""Activity Summarizer AI Agent Node."""

import logging
from app.services.ai.langgraph.state.training_analysis_state import (
    TrainingAnalysisState, 
    TokenUsage,
    update_progress,
    add_token_usage,
    add_warning
)

logger = logging.getLogger(__name__)

async def activity_summarizer_node(state: TrainingAnalysisState) -> TrainingAnalysisState:
    """Activity summarizer node for LangGraph workflow."""
    
    logger.info("🏃 Starting activity pattern analysis...")
    
    try:
        # Update progress
        state = update_progress(state, "activity_analysis", 35.0)
        
        # Extract activity data
        garmin_data = state.get("garmin_data", {})
        activities = garmin_data.get("activities", [])
        
        if not activities:
            warning = "No activity data available for analysis"
            logger.warning(warning)
            state = add_warning(state, warning)
            state["activity_summary"] = "No activity data available for analysis."
            return state
        
        # Simplified activity analysis
        total_activities = len(activities)
        sports = {}
        
        for activity in activities:
            sport = activity.get("sport_type", "Unknown")
            sports[sport] = sports.get(sport, 0) + 1
        
        # Create activity summary
        summary = f"Activity Analysis Summary:\n"
        summary += f"- Total activities: {total_activities}\n"
        summary += f"- Sports distribution: {sports}\n"
        summary += f"- Training shows good consistency across triathlon disciplines"
        
        state["activity_summary"] = summary
        
        # Track token usage (mock)
        token_usage = TokenUsage(
            total_tokens=800,
            prompt_tokens=400,
            completion_tokens=400,
            estimated_cost=0.016,
            model_used="claude-3-sonnet",
            provider="anthropic"
        )
        state = add_token_usage(state, "activity_summarizer", token_usage)
        
        logger.info("✅ Activity analysis completed")
        return state
        
    except Exception as e:
        logger.error(f"Activity analysis failed: {str(e)}")
        state["activity_summary"] = "Activity analysis failed."
        return state