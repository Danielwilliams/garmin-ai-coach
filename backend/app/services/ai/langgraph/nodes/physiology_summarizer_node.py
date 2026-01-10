"""Physiology Summarizer AI Agent - Recovery & Physiological Data Analysis.

This agent replicates the CLI's physiology summarizer with the same
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


class PhysiologySummarizerAgent:
    """AI agent for summarizing physiological and recovery data."""
    
    def __init__(self):
        self.agent_name = "physiology_summarizer"
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the agent's role and expertise."""
        
        return """You are an AI expert specializing in exercise physiology and recovery analysis for triathlon athletes. Your role is to analyze and summarize physiological data with a focus on:

CORE EXPERTISE:
- Recovery patterns and adaptation indicators
- Sleep quality and recovery metrics
- Heart rate variability (HRV) analysis
- Stress and readiness assessment
- Physiological adaptation markers
- Body composition and health metrics

ANALYSIS FOCUS:
- Recovery adequacy and patterns
- Training adaptation indicators
- Stress accumulation and management
- Sleep quality and recovery impact
- HRV trends and autonomic balance
- Physiological readiness for training
- Body composition changes

INPUT DATA TYPES:
- Recovery indicators (HRV, sleep scores, etc.)
- Body battery and stress levels
- Sleep data (duration, quality, stages)
- Physiological markers (VO2, body composition)
- Heart rate variability metrics
- Stress and readiness indicators
- Body weight and composition trends

OUTPUT REQUIREMENTS:
- Concise summary of recovery patterns
- Assessment of physiological adaptation
- Identification of stress accumulation
- Sleep quality and recovery analysis
- HRV trends and autonomic status
- Body composition and health insights
- Recovery adequacy for training load

ANALYSIS PRINCIPLES:
- Emphasize recovery-performance relationship
- Focus on adaptation vs maladaptation indicators
- Consider individual baseline variations
- Identify patterns over isolated measurements
- Balance autonomic nervous system indicators
- Relate physiological state to training capacity

Be thorough but concise. Focus on recovery and physiological patterns that will inform training decisions and workload management."""

    async def process_physiology_data(self, state: TrainingAnalysisState) -> TrainingAnalysisState:
        """Process and summarize physiological and recovery data."""
        
        try:
            logger.info(f"🫀 Starting physiology summarization for analysis {state['analysis_id']}")
            
            # Update progress
            state = update_progress(state, "physiology_summarization", 15.0)
            
            # Extract relevant data from state
            garmin_data = state.get("garmin_data", {})
            training_config = state.get("training_config", {})
            user_profile = state.get("user_profile", {})
            
            # Prepare data for AI analysis
            physiology_context = self._prepare_physiology_context(
                garmin_data, training_config, user_profile
            )
            
            # Generate AI summary
            summary = await self._generate_ai_summary(physiology_context, state)
            
            # Store result in state
            state["physiology_summary"] = summary
            
            logger.info(f"✅ Physiology summarization completed for {state['analysis_id']}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Physiology summarization failed: {e}")
            return add_error(state, f"Physiology summarization failed: {str(e)}")
    
    def _prepare_physiology_context(
        self, 
        garmin_data: Dict[str, Any],
        training_config: Dict[str, Any], 
        user_profile: Dict[str, Any]
    ) -> str:
        """Prepare physiological context for AI analysis."""
        
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
            context_parts.append("\n=== ANALYSIS CONTEXT ===")
            context_parts.append(f"Analysis Period: {training_config.get('metrics_days', 56)} days")
            context_parts.append(f"Training Focus: {training_config.get('analysis_context', 'General training')}")
        
        # Add recovery indicators
        if garmin_data and 'recovery_indicators' in garmin_data:
            context_parts.append(self._format_recovery_indicators(garmin_data['recovery_indicators']))
        
        # Add physiological markers
        if garmin_data and 'physiological_markers' in garmin_data:
            context_parts.append(self._format_physiological_markers(garmin_data['physiological_markers']))
        
        # Add daily stats (sleep, stress, etc.)
        if garmin_data and 'daily_stats' in garmin_data:
            context_parts.append(self._format_daily_wellness(garmin_data['daily_stats']))
        
        # Add body metrics
        if garmin_data and 'body_metrics' in garmin_data:
            context_parts.append(self._format_body_metrics(garmin_data['body_metrics']))
        
        return "\n".join(context_parts)
    
    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date."""
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except:
            return 0
    
    def _format_recovery_indicators(self, recovery_data: list) -> str:
        """Format recovery indicators for analysis."""
        
        if not recovery_data:
            return "\n=== RECOVERY DATA ===\nNo recovery data available"
        
        parts = ["\n=== RECOVERY INDICATORS ==="]
        
        # Get recent data (last 14 days)
        recent_data = recovery_data[-14:] if len(recovery_data) >= 14 else recovery_data
        
        # HRV Analysis
        hrv_values = [d.get('hrv_rmssd') for d in recent_data if d.get('hrv_rmssd')]
        if hrv_values:
            avg_hrv = sum(hrv_values) / len(hrv_values)
            latest_hrv = hrv_values[-1]
            parts.append(f"HRV (RMSSD): Latest {latest_hrv:.1f}ms, 14-day avg {avg_hrv:.1f}ms")
        
        # Training Readiness
        readiness_values = [d.get('training_readiness') for d in recent_data if d.get('training_readiness')]
        if readiness_values:
            avg_readiness = sum(readiness_values) / len(readiness_values)
            latest_readiness = readiness_values[-1]
            parts.append(f"Training Readiness: Latest {latest_readiness}, 14-day avg {avg_readiness:.1f}")
        
        # Sleep Scores
        sleep_scores = [d.get('sleep_score') for d in recent_data if d.get('sleep_score')]
        if sleep_scores:
            avg_sleep = sum(sleep_scores) / len(sleep_scores)
            latest_sleep = sleep_scores[-1]
            parts.append(f"Sleep Score: Latest {latest_sleep}, 14-day avg {avg_sleep:.1f}")
        
        # Stress Levels
        stress_scores = [d.get('stress_score') for d in recent_data if d.get('stress_score')]
        if stress_scores:
            avg_stress = sum(stress_scores) / len(stress_scores)
            latest_stress = stress_scores[-1]
            parts.append(f"Stress Score: Latest {latest_stress}, 14-day avg {avg_stress:.1f}")
        
        # Body Battery
        body_battery_charged = [d.get('body_battery_charged') for d in recent_data if d.get('body_battery_charged')]
        body_battery_drained = [d.get('body_battery_drained') for d in recent_data if d.get('body_battery_drained')]
        
        if body_battery_charged and body_battery_drained:
            avg_charged = sum(body_battery_charged) / len(body_battery_charged)
            avg_drained = sum(body_battery_drained) / len(body_battery_drained)
            net_recovery = avg_charged - avg_drained
            parts.append(f"Body Battery: Avg charged {avg_charged:.0f}, drained {avg_drained:.0f}, net {net_recovery:+.0f}")
        
        # SpO2
        spo2_values = [d.get('spo2_average') for d in recent_data if d.get('spo2_average')]
        if spo2_values:
            avg_spo2 = sum(spo2_values) / len(spo2_values)
            parts.append(f"SpO2 Average: {avg_spo2:.1f}%")
        
        return "\n".join(parts)
    
    def _format_physiological_markers(self, physio_markers: list) -> str:
        """Format physiological markers for analysis."""
        
        if not physio_markers:
            return ""
        
        latest_marker = physio_markers[-1] if physio_markers else {}
        
        parts = ["\n=== PHYSIOLOGICAL MARKERS ==="]
        
        if latest_marker.get('vo2_max'):
            parts.append(f"VO2 Max: {latest_marker['vo2_max']}")
        
        if latest_marker.get('body_battery'):
            parts.append(f"Body Battery: {latest_marker['body_battery']}")
        
        if latest_marker.get('stress_level'):
            parts.append(f"Stress Level: {latest_marker['stress_level']}")
        
        if latest_marker.get('recovery_time_hours'):
            parts.append(f"Recovery Time: {latest_marker['recovery_time_hours']} hours")
        
        if latest_marker.get('training_stress_balance'):
            tsb = latest_marker['training_stress_balance']
            parts.append(f"Training Stress Balance: {tsb} ({'Fresh' if tsb > 0 else 'Fatigued'})")
        
        return "\n".join(parts)
    
    def _format_daily_wellness(self, daily_stats: list) -> str:
        """Format daily wellness data for analysis."""
        
        if not daily_stats:
            return ""
        
        parts = ["\n=== DAILY WELLNESS TRENDS ==="]
        
        # Get recent data (last 14 days)
        recent_stats = daily_stats[-14:] if len(daily_stats) >= 14 else daily_stats
        
        # Resting Heart Rate Trend
        rhr_values = [d.get('resting_heart_rate') for d in recent_stats if d.get('resting_heart_rate')]
        if rhr_values:
            avg_rhr = sum(rhr_values) / len(rhr_values)
            latest_rhr = rhr_values[-1]
            trend = "increasing" if latest_rhr > avg_rhr else "decreasing"
            parts.append(f"Resting HR: Latest {latest_rhr} bpm, 14-day avg {avg_rhr:.1f} bpm ({trend})")
        
        # Sleep Duration Trend
        sleep_values = [d.get('sleep_hours') for d in recent_stats if d.get('sleep_hours')]
        if sleep_values:
            avg_sleep = sum(sleep_values) / len(sleep_values)
            latest_sleep = sleep_values[-1]
            parts.append(f"Sleep Duration: Latest {latest_sleep:.1f}h, 14-day avg {avg_sleep:.1f}h")
        
        # Steps and Activity
        steps_values = [d.get('steps') for d in recent_stats if d.get('steps')]
        if steps_values:
            avg_steps = sum(steps_values) / len(steps_values)
            parts.append(f"Daily Steps: 14-day avg {avg_steps:,.0f}")
        
        return "\n".join(parts)
    
    def _format_body_metrics(self, body_metrics: list) -> str:
        """Format body composition metrics for analysis."""
        
        if not body_metrics:
            return ""
        
        parts = ["\n=== BODY COMPOSITION ==="]
        
        # Weight trend
        weight_values = [m.get('weight_kg') for m in body_metrics if m.get('weight_kg')]
        if weight_values:
            if len(weight_values) >= 2:
                weight_change = weight_values[-1] - weight_values[0]
                parts.append(f"Weight: {weight_values[-1]:.1f} kg (change: {weight_change:+.1f} kg)")
            else:
                parts.append(f"Weight: {weight_values[-1]:.1f} kg")
        
        # Body fat
        latest_metrics = body_metrics[-1] if body_metrics else {}
        if latest_metrics.get('body_fat_percentage'):
            parts.append(f"Body Fat: {latest_metrics['body_fat_percentage']:.1f}%")
        
        if latest_metrics.get('bmi'):
            parts.append(f"BMI: {latest_metrics['bmi']:.1f}")
        
        return "\n".join(parts)
    
    async def _generate_ai_summary(self, context: str, state: TrainingAnalysisState) -> str:
        """Generate AI summary of physiological data."""
        
        try:
            # Get AI model for this agent
            model_manager = get_model_manager()
            client = model_manager.get_agent_client(self.agent_name)
            
            # Create the prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", """Please analyze the following physiological and recovery data and provide a comprehensive summary focusing on recovery patterns, adaptation indicators, and physiological readiness:

{context}

Provide a structured summary that includes:
1. Recovery pattern analysis (HRV, sleep, stress trends)
2. Training adaptation and physiological markers
3. Autonomic balance and stress management
4. Sleep quality and recovery adequacy
5. Body composition and health indicators
6. Overall physiological readiness assessment

Focus on recovery-performance relationships and patterns that inform training capacity and workload management.""")
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
            
            logger.info(f"🫀 Generated physiology summary: {len(summary)} characters")
            return summary
            
        except Exception as e:
            logger.error(f"❌ AI summary generation failed: {e}")
            raise


# Node function for LangGraph integration
async def physiology_summarizer_node(state: TrainingAnalysisState) -> TrainingAnalysisState:
    """LangGraph node function for physiology summarization."""
    
    agent = PhysiologySummarizerAgent()
    return await agent.process_physiology_data(state)