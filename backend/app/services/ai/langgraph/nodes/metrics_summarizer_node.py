"""Metrics Summarizer AI Agent - Training Load & Fitness Metrics Analysis.

This agent replicates the CLI's metrics summarizer with the same
AI prompts, processing logic, and output format.
"""

from typing import Dict, Any, Optional
from datetime import datetime
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


class MetricsSummarizerAgent:
    """AI agent for summarizing training metrics and fitness data."""
    
    def __init__(self):
        self.agent_name = "metrics_summarizer"
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the agent's role and expertise.
        
        This matches the CLI's metrics summarizer prompt exactly.
        """
        
        return """You are an AI expert specializing in training load analysis and fitness metrics for triathlon athletes. Your role is to analyze and summarize training data with a focus on:

CORE EXPERTISE:
- Training load patterns and trends
- Fitness progression indicators  
- Performance metrics analysis
- Training stress and recovery balance
- Volume and intensity distribution
- Power, pace, and heart rate analysis

ANALYSIS FOCUS:
- Acute vs chronic training load
- Training stress balance (TSB)
- Fitness peaks and valleys
- Workload progression patterns
- Recovery adequacy indicators
- Performance benchmarking

INPUT DATA TYPES:
- Daily training statistics
- Activity summaries with power/pace/HR
- Training stress scores (TSS)
- Physiological markers (VO2, FTP, etc.)
- Heart rate zone distribution
- Training volume and frequency

OUTPUT REQUIREMENTS:
- Concise summary of key training load patterns
- Identification of fitness trends and adaptations
- Assessment of training stress balance
- Highlight notable metrics changes
- Flag potential overreaching/undertraining
- Provide context for expert analysis

ANALYSIS PRINCIPLES:
- Focus on actionable insights
- Emphasize trend analysis over single data points
- Consider training phase and goals context
- Identify both positive adaptations and concerns
- Maintain scientific accuracy with practical relevance

Be thorough but concise. Focus on patterns that will inform subsequent expert analysis and training recommendations."""

    async def process_metrics_data(self, state: TrainingAnalysisState) -> TrainingAnalysisState:
        """Process and summarize training metrics data.
        
        This is the main entry point that matches the CLI node structure.
        """
        
        try:
            logger.info(f"🔢 Starting metrics summarization for analysis {state['analysis_id']}")
            
            # Update progress
            state = update_progress(state, "metrics_summarization", 15.0)
            
            # Extract relevant data from state
            garmin_data = state.get("garmin_data", {})
            training_config = state.get("training_config", {})
            user_profile = state.get("user_profile", {})
            
            # Prepare data for AI analysis
            metrics_context = self._prepare_metrics_context(
                garmin_data, training_config, user_profile
            )
            
            # Generate AI summary
            summary = await self._generate_ai_summary(metrics_context, state)
            
            # Store result in state
            state["metrics_summary"] = summary
            
            logger.info(f"✅ Metrics summarization completed for {state['analysis_id']}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Metrics summarization failed: {e}")
            return add_error(state, f"Metrics summarization failed: {str(e)}")
    
    def _prepare_metrics_context(
        self, 
        garmin_data: Dict[str, Any],
        training_config: Dict[str, Any], 
        user_profile: Dict[str, Any]
    ) -> str:
        """Prepare training metrics context for AI analysis."""
        
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
        
        # Add data overview
        if garmin_data:
            context_parts.append(f"\n=== DATA OVERVIEW ===")
            context_parts.append(garmin_data.get('activity_summary_text', 'No activity data available'))
            
            # Add detailed metrics if available
            if 'physiological_markers' in garmin_data:
                context_parts.append(self._format_physiological_data(garmin_data['physiological_markers']))
            
            if 'training_status' in garmin_data:
                context_parts.append(self._format_training_status(garmin_data['training_status']))
            
            if 'activities' in garmin_data:
                context_parts.append(self._format_activity_metrics(garmin_data['activities']))
        
        return "\n".join(context_parts)
    
    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date."""
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except:
            return 0
    
    def _format_physiological_data(self, physio_markers: list) -> str:
        """Format physiological markers for analysis."""
        
        if not physio_markers:
            return ""
        
        latest_marker = physio_markers[-1] if physio_markers else {}
        
        parts = ["\n=== PHYSIOLOGICAL MARKERS ==="]
        
        if latest_marker.get('vo2_max'):
            parts.append(f"VO2 Max: {latest_marker['vo2_max']}")
        
        if latest_marker.get('functional_threshold_power'):
            parts.append(f"FTP: {latest_marker['functional_threshold_power']}W")
        
        if latest_marker.get('lactate_threshold_heart_rate'):
            parts.append(f"LT HR: {latest_marker['lactate_threshold_heart_rate']} bpm")
        
        if latest_marker.get('training_stress_balance'):
            parts.append(f"Training Stress Balance: {latest_marker['training_stress_balance']}")
        
        if latest_marker.get('acute_load'):
            parts.append(f"Acute Load: {latest_marker['acute_load']}")
        
        if latest_marker.get('chronic_load'):
            parts.append(f"Chronic Load: {latest_marker['chronic_load']}")
        
        return "\n".join(parts)
    
    def _format_training_status(self, training_status: list) -> str:
        """Format training status for analysis."""
        
        if not training_status:
            return ""
        
        latest_status = training_status[-1] if training_status else {}
        
        parts = ["\n=== TRAINING STATUS ==="]
        
        if latest_status.get('training_status'):
            parts.append(f"Current Status: {latest_status['training_status']}")
        
        if latest_status.get('load_ratio'):
            parts.append(f"Load Ratio: {latest_status['load_ratio']}")
        
        if latest_status.get('training_effect_aerobic'):
            parts.append(f"Aerobic TE: {latest_status['training_effect_aerobic']}")
        
        if latest_status.get('training_effect_anaerobic'):
            parts.append(f"Anaerobic TE: {latest_status['training_effect_anaerobic']}")
        
        if latest_status.get('recovery_time'):
            parts.append(f"Recovery Time: {latest_status['recovery_time']} hours")
        
        return "\n".join(parts)
    
    def _format_activity_metrics(self, activities: list) -> str:
        """Format activity metrics for analysis."""
        
        if not activities:
            return ""
        
        # Calculate aggregate metrics
        total_activities = len(activities)
        avg_tss = sum(a.get('training_stress_score', 0) for a in activities) / total_activities if total_activities > 0 else 0
        avg_hr = sum(a.get('average_heart_rate', 0) for a in activities if a.get('average_heart_rate')) / max(1, len([a for a in activities if a.get('average_heart_rate')]))
        
        # Activity type distribution
        activity_types = {}
        for activity in activities:
            activity_type = activity.get('activity_type', 'unknown')
            activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
        
        parts = ["\n=== ACTIVITY METRICS ==="]
        parts.append(f"Total Activities: {total_activities}")
        parts.append(f"Average TSS: {avg_tss:.1f}")
        parts.append(f"Average HR: {avg_hr:.0f} bpm")
        
        if activity_types:
            type_summary = ", ".join([f"{type_name}: {count}" for type_name, count in activity_types.items()])
            parts.append(f"Activity Distribution: {type_summary}")
        
        # Recent trend (last 7 activities)
        recent_activities = activities[-7:] if len(activities) >= 7 else activities
        if recent_activities:
            recent_tss = sum(a.get('training_stress_score', 0) for a in recent_activities) / len(recent_activities)
            parts.append(f"Recent TSS Trend: {recent_tss:.1f}")
        
        return "\n".join(parts)
    
    async def _generate_ai_summary(self, context: str, state: TrainingAnalysisState) -> str:
        """Generate AI summary of training metrics."""
        
        try:
            # Get AI model for this agent
            model_manager = get_model_manager()
            client = model_manager.get_agent_client(self.agent_name)
            
            # Create the prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", """Please analyze the following training data and provide a comprehensive summary focusing on training load patterns, fitness trends, and key metrics insights:

{context}

Provide a structured summary that includes:
1. Training load analysis (volume, intensity, distribution)
2. Fitness progression indicators and trends
3. Training stress balance assessment
4. Notable metrics changes or patterns
5. Key insights for expert analysis

Focus on actionable insights and patterns that inform training decisions.""")
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
            
            logger.info(f"📊 Generated metrics summary: {len(summary)} characters")
            return summary
            
        except Exception as e:
            logger.error(f"❌ AI summary generation failed: {e}")
            raise


# Node function for LangGraph integration
async def metrics_summarizer_node(state: TrainingAnalysisState) -> TrainingAnalysisState:
    """LangGraph node function for metrics summarization."""
    
    agent = MetricsSummarizerAgent()
    return await agent.process_metrics_data(state)