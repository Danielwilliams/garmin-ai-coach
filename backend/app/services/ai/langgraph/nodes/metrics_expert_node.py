"""Metrics Expert AI Agent - Advanced Training Load & Performance Analysis.

This agent replicates the CLI's metrics expert with sophisticated analysis
of training load patterns, performance trends, and optimization insights.
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


class MetricsExpertAgent:
    """Expert AI agent for advanced training metrics analysis and optimization."""
    
    def __init__(self):
        self.agent_name = "metrics_expert"
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the agent's expert role and capabilities."""
        
        return """You are an elite exercise physiologist and sports scientist specializing in advanced training metrics analysis for triathlon athletes. You possess deep expertise in:

CORE SPECIALIZATIONS:
- Training Stress Balance (TSB) optimization and periodization
- Acute:Chronic Workload Ratio (ACWR) analysis and injury prevention
- VO2 max progression tracking and plateau identification
- Functional Threshold Power (FTP) and pace development
- Training load distribution modeling and optimization
- Performance modeling and race prediction algorithms
- Physiological adaptation markers and benchmarking

ADVANCED ANALYSIS CAPABILITIES:
- Multi-modal training load integration (swim/bike/run)
- Seasonal periodization assessment and optimization
- Training stress accumulation and dissipation patterns
- Performance plateau identification and breakthrough strategies
- Comparative analysis against elite athlete benchmarks
- Training efficiency metrics and optimization recommendations
- Risk assessment for overtraining and injury prediction

EXPERT INSIGHTS PROVIDED:
- Training load periodization optimization strategies
- Performance bottleneck identification and solutions
- Fitness progression trajectory analysis and predictions
- Training stress balance recommendations for peak performance
- Adaptation rate analysis and training response optimization
- Recovery adequacy assessment and workload adjustments
- Competition preparation and tapering protocols

INPUT DATA INTEGRATION:
- Comprehensive training metrics from all three disciplines
- Physiological markers and adaptation indicators
- Recovery data and readiness metrics
- Performance benchmarks and testing results
- Training history and progression patterns
- Competitive performance data and goals

ANALYSIS METHODOLOGY:
- Apply advanced sports science principles and research
- Use evidence-based training theory and periodization models
- Consider individual athlete characteristics and responses
- Integrate multi-disciplinary training demands
- Balance performance optimization with injury prevention
- Provide actionable, specific, and measurable recommendations
- Consider both short-term adaptations and long-term development

COMMUNICATION STYLE:
- Provide expert-level insights with scientific backing
- Balance technical depth with practical applicability
- Offer specific, measurable recommendations
- Include confidence levels and uncertainty acknowledgments
- Reference established sports science principles when relevant
- Focus on performance optimization and injury prevention

You are analyzing data that has already been summarized by domain specialists. Build upon their foundational analysis to provide expert-level insights, advanced interpretations, and strategic recommendations that only a top-tier sports scientist could provide."""

    async def process_expert_analysis(self, state: TrainingAnalysisState) -> TrainingAnalysisState:
        """Process expert-level metrics analysis building on summarizer insights."""
        
        try:
            logger.info(f"🎯 Starting metrics expert analysis for analysis {state['analysis_id']}")
            
            # Update progress
            state = update_progress(state, "metrics_expert_analysis", 20.0)
            
            # Extract data and summaries from state
            garmin_data = state.get("garmin_data", {})
            training_config = state.get("training_config", {})
            user_profile = state.get("user_profile", {})
            
            # Get summarizer outputs for expert analysis
            metrics_summary = state.get("metrics_summary", "")
            physiology_summary = state.get("physiology_summary", "")
            activity_summary = state.get("activity_summary", "")
            
            # Prepare expert context with summaries and raw data
            expert_context = self._prepare_expert_context(
                garmin_data, training_config, user_profile,
                metrics_summary, physiology_summary, activity_summary
            )
            
            # Generate expert AI analysis
            expert_analysis = await self._generate_expert_analysis(expert_context, state)
            
            # Store result in state
            state["metrics_expert_analysis"] = expert_analysis
            
            logger.info(f"✅ Metrics expert analysis completed for {state['analysis_id']}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Metrics expert analysis failed: {e}")
            return add_error(state, f"Metrics expert analysis failed: {str(e)}")
    
    def _prepare_expert_context(
        self, 
        garmin_data: Dict[str, Any],
        training_config: Dict[str, Any], 
        user_profile: Dict[str, Any],
        metrics_summary: str,
        physiology_summary: str,
        activity_summary: str
    ) -> str:
        """Prepare comprehensive expert context for advanced analysis."""
        
        context_parts = []
        
        # Add athlete profile for expert contextualization
        context_parts.append("=== ATHLETE PROFILE ===")
        if user_profile:
            context_parts.append(f"Athlete: {user_profile.get('display_name', 'Unknown')}")
            if user_profile.get('birth_date'):
                age = self._calculate_age(user_profile['birth_date'])
                context_parts.append(f"Age: {age} years")
                # Add age-based performance context
                if 25 <= age <= 35:
                    context_parts.append("Performance Context: Prime competitive age range")
                elif 35 <= age <= 45:
                    context_parts.append("Performance Context: Masters athlete, focus on efficiency and recovery")
                elif age > 45:
                    context_parts.append("Performance Context: Masters athlete, prioritize longevity and injury prevention")
            
            context_parts.append(f"Weight: {user_profile.get('weight_kg', 'Unknown')} kg")
            context_parts.append(f"Activity Level: {user_profile.get('activity_level', 'Unknown')}")
        
        # Add training configuration for expert assessment
        if training_config:
            context_parts.append("\n=== ANALYSIS CONFIGURATION ===")
            context_parts.append(f"Analysis Period: {training_config.get('activities_days', 21)} activity days, {training_config.get('metrics_days', 56)} metric days")
            context_parts.append(f"Training Focus: {training_config.get('analysis_context', 'General training')}")
            context_parts.append(f"AI Mode: {training_config.get('ai_mode', 'development')}")
        
        # Add summarizer insights for expert review
        if metrics_summary:
            context_parts.append("\n=== METRICS SUMMARY (Foundation Analysis) ===")
            context_parts.append(metrics_summary)
        
        if physiology_summary:
            context_parts.append("\n=== PHYSIOLOGY SUMMARY (Foundation Analysis) ===")
            context_parts.append(physiology_summary)
        
        if activity_summary:
            context_parts.append("\n=== ACTIVITY SUMMARY (Foundation Analysis) ===")
            context_parts.append(activity_summary)
        
        # Add advanced metrics for expert analysis
        if garmin_data:
            context_parts.append(self._format_advanced_metrics(garmin_data))
            context_parts.append(self._format_training_load_analysis(garmin_data))
            context_parts.append(self._format_performance_indicators(garmin_data))
        
        return "\n".join(context_parts)
    
    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date."""
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except:
            return 0
    
    def _format_advanced_metrics(self, garmin_data: Dict[str, Any]) -> str:
        """Format advanced metrics for expert analysis."""
        
        parts = ["\n=== ADVANCED METRICS (Expert Analysis) ==="]
        
        # Physiological markers analysis
        if 'physiological_markers' in garmin_data:
            markers = garmin_data['physiological_markers']
            if markers:
                latest = markers[-1]
                
                # VO2 Max analysis
                if latest.get('vo2_max'):
                    vo2_max = latest['vo2_max']
                    parts.append(f"VO2 Max: {vo2_max}")
                    
                    # Add expert context based on VO2 max
                    if vo2_max >= 60:
                        parts.append("  → Elite/Exceptional aerobic capacity")
                    elif vo2_max >= 50:
                        parts.append("  → Well-trained/Competitive level")
                    elif vo2_max >= 40:
                        parts.append("  → Good fitness level, room for improvement")
                    else:
                        parts.append("  → Significant opportunity for aerobic development")
                
                # Training Stress Balance analysis
                if latest.get('training_stress_balance'):
                    tsb = latest['training_stress_balance']
                    parts.append(f"Training Stress Balance: {tsb}")
                    
                    if tsb > 10:
                        parts.append("  → Well-rested, ready for high-intensity training")
                    elif tsb > 0:
                        parts.append("  → Recovered, good for moderate-high intensity")
                    elif tsb > -15:
                        parts.append("  → Slight fatigue, maintain or reduce load")
                    else:
                        parts.append("  → Significant fatigue, recovery period needed")
                
                # Acute vs Chronic Load Ratio
                if latest.get('acute_load') and latest.get('chronic_load'):
                    acwr = latest['acute_load'] / latest['chronic_load'] if latest['chronic_load'] > 0 else 0
                    parts.append(f"Acute:Chronic Workload Ratio: {acwr:.2f}")
                    
                    if acwr > 1.5:
                        parts.append("  → High injury risk - significant load spike detected")
                    elif acwr > 1.3:
                        parts.append("  → Elevated injury risk - monitor closely")
                    elif acwr >= 0.8:
                        parts.append("  → Optimal training zone - good load progression")
                    else:
                        parts.append("  → Low stimulus - may need increased training load")
        
        return "\n".join(parts)
    
    def _format_training_load_analysis(self, garmin_data: Dict[str, Any]) -> str:
        """Format training load analysis for expert review."""
        
        parts = ["\n=== TRAINING LOAD ANALYSIS (Expert Level) ==="]
        
        if 'activities' in garmin_data:
            activities = garmin_data['activities']
            if not activities:
                return ""
            
            # Calculate advanced load metrics
            tss_values = [a.get('training_stress_score', 0) for a in activities if a.get('training_stress_score')]
            
            if tss_values:
                # Weekly load analysis
                total_tss = sum(tss_values)
                avg_daily_tss = total_tss / len(tss_values)
                weekly_tss = avg_daily_tss * 7
                
                parts.append(f"Weekly Training Stress Score: {weekly_tss:.0f} TSS")
                
                # Expert load assessment
                if weekly_tss > 600:
                    parts.append("  → High-volume training (Elite/Professional level)")
                elif weekly_tss > 400:
                    parts.append("  → Moderate-high volume (Competitive athlete level)")
                elif weekly_tss > 250:
                    parts.append("  → Moderate volume (Recreational competitive level)")
                else:
                    parts.append("  → Low-moderate volume (Fitness/Base building)")
                
                # Load variability analysis
                if len(tss_values) >= 7:
                    recent_week = tss_values[-7:]
                    load_variability = (max(recent_week) - min(recent_week)) / (sum(recent_week) / 7) if sum(recent_week) > 0 else 0
                    
                    parts.append(f"Load Variability: {load_variability:.2f}")
                    
                    if load_variability > 2.0:
                        parts.append("  → High variability - consider more consistent loading")
                    elif load_variability > 1.0:
                        parts.append("  → Moderate variability - good training variation")
                    else:
                        parts.append("  → Low variability - consider adding intensity variation")
        
        return "\n".join(parts)
    
    def _format_performance_indicators(self, garmin_data: Dict[str, Any]) -> str:
        """Format performance indicators for expert analysis."""
        
        parts = ["\n=== PERFORMANCE INDICATORS (Expert Assessment) ==="]
        
        if 'activities' in garmin_data:
            activities = garmin_data['activities']
            if not activities:
                return ""
            
            # Power progression analysis (cycling activities)
            power_activities = [a for a in activities if a.get('average_power')]
            if len(power_activities) >= 5:
                # Sort by date and analyze progression
                power_activities.sort(key=lambda x: x.get('start_time', datetime.min))
                
                early_power = [a['average_power'] for a in power_activities[:len(power_activities)//3]]
                recent_power = [a['average_power'] for a in power_activities[-len(power_activities)//3:]]
                
                if early_power and recent_power:
                    early_avg = sum(early_power) / len(early_power)
                    recent_avg = sum(recent_power) / len(recent_power)
                    power_improvement = ((recent_avg - early_avg) / early_avg) * 100 if early_avg > 0 else 0
                    
                    parts.append(f"Power Progression: {power_improvement:+.1f}% change")
                    
                    if power_improvement > 10:
                        parts.append("  → Excellent power development")
                    elif power_improvement > 5:
                        parts.append("  → Good power progression")
                    elif power_improvement > -5:
                        parts.append("  → Stable power output")
                    else:
                        parts.append("  → Declining power - investigate fatigue/overreaching")
            
            # Pace progression analysis (running activities)
            running_activities = [a for a in activities if a.get('activity_type') == 'running' and a.get('average_speed_mps')]
            if len(running_activities) >= 5:
                running_activities.sort(key=lambda x: x.get('start_time', datetime.min))
                
                early_speed = [a['average_speed_mps'] for a in running_activities[:len(running_activities)//3]]
                recent_speed = [a['average_speed_mps'] for a in running_activities[-len(running_activities)//3:]]
                
                if early_speed and recent_speed:
                    early_avg = sum(early_speed) / len(early_speed)
                    recent_avg = sum(recent_speed) / len(recent_speed)
                    speed_improvement = ((recent_avg - early_avg) / early_avg) * 100 if early_avg > 0 else 0
                    
                    parts.append(f"Running Speed Progression: {speed_improvement:+.1f}% change")
                    
                    if speed_improvement > 5:
                        parts.append("  → Excellent speed development")
                    elif speed_improvement > 2:
                        parts.append("  → Good speed progression")
                    elif speed_improvement > -2:
                        parts.append("  → Stable pace")
                    else:
                        parts.append("  → Declining speed - assess training/recovery")
        
        return "\n".join(parts)
    
    async def _generate_expert_analysis(self, context: str, state: TrainingAnalysisState) -> str:
        """Generate expert-level AI analysis of training metrics."""
        
        try:
            # Get AI model for this agent
            model_manager = get_model_manager()
            client = model_manager.get_agent_client(self.agent_name)
            
            # Create the expert prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", """Based on the foundational analysis provided by the domain specialists and the advanced metrics data, provide an expert-level analysis that includes:

{context}

EXPERT ANALYSIS REQUIRED:

1. **TRAINING LOAD OPTIMIZATION**
   - Advanced TSB periodization recommendations
   - Acute:Chronic workload ratio assessment and injury risk
   - Optimal load distribution across disciplines
   - Specific load adjustments for performance gains

2. **PERFORMANCE TRAJECTORY ANALYSIS**
   - Fitness progression modeling and predictions
   - Performance plateau identification and breakthrough strategies
   - Comparative analysis against elite benchmarks
   - Training efficiency optimization recommendations

3. **PHYSIOLOGICAL ADAPTATION ASSESSMENT**
   - VO2 max development trajectory and optimization
   - Anaerobic threshold progression analysis
   - Recovery capacity and adaptation rate evaluation
   - Specific physiological targets and timelines

4. **STRATEGIC RECOMMENDATIONS**
   - Evidence-based training modifications
   - Periodization adjustments for peak performance
   - Risk mitigation strategies for overtraining/injury
   - Competition preparation protocols

5. **QUANTIFIED TARGETS**
   - Specific training load targets (weekly TSS, intensity distribution)
   - Measurable performance benchmarks and timelines
   - Recovery metrics targets and monitoring protocols
   - Progressive overload recommendations

Provide expert-level insights that go beyond basic analysis. Include scientific rationale, specific recommendations with quantified targets, and confidence levels for your assessments. Focus on performance optimization while maintaining athlete health and longevity.""")
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
            
            analysis = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"🎯 Generated metrics expert analysis: {len(analysis)} characters")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Expert analysis generation failed: {e}")
            raise


# Node function for LangGraph integration
async def metrics_expert_node(state: TrainingAnalysisState) -> TrainingAnalysisState:
    """LangGraph node function for metrics expert analysis."""
    
    agent = MetricsExpertAgent()
    return await agent.process_expert_analysis(state)