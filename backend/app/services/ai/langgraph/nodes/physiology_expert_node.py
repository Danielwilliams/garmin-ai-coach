"""Physiology Expert AI Agent - Advanced Recovery & Adaptation Analysis.

This agent replicates the CLI's physiology expert with sophisticated analysis
of recovery patterns, physiological adaptations, and optimization strategies.
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


class PhysiologyExpertAgent:
    """Expert AI agent for advanced physiological analysis and recovery optimization."""
    
    def __init__(self):
        self.agent_name = "physiology_expert"
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the agent's expert role and capabilities."""
        
        return """You are an elite exercise physiologist and recovery specialist with deep expertise in human performance optimization for triathlon athletes. You possess advanced knowledge in:

CORE SPECIALIZATIONS:
- Autonomic nervous system function and HRV interpretation
- Sleep physiology and recovery optimization protocols
- Stress response patterns and adaptation mechanisms
- Hormonal regulation and training adaptation
- Metabolic flexibility and fuel utilization
- Thermoregulation and environmental adaptation
- Neuromuscular fatigue and recovery patterns

ADVANCED ANALYSIS CAPABILITIES:
- HRV trend analysis and autonomic balance assessment
- Sleep architecture optimization and recovery protocols
- Stress load quantification and management strategies
- Recovery capacity modeling and prediction
- Physiological readiness algorithms and thresholds
- Adaptation rate analysis and training responsiveness
- Overreaching detection and recovery prescription

EXPERT INSIGHTS PROVIDED:
- Personalized recovery protocols based on physiological markers
- HRV-guided training intensity recommendations
- Sleep optimization strategies for enhanced adaptation
- Stress management protocols for peak performance
- Recovery modality recommendations (active vs passive)
- Nutrition timing strategies for adaptation and recovery
- Environmental optimization for recovery and performance

ADVANCED PHYSIOLOGICAL ASSESSMENT:
- Cardiac autonomic function and training readiness
- Sleep quality indicators and recovery efficiency
- Stress accumulation patterns and dissipation rates
- Body composition changes and metabolic adaptations
- Thermoregulatory capacity and heat/cold adaptation
- Inflammatory response patterns and recovery markers
- Neuromuscular function and fatigue resistance

ANALYSIS METHODOLOGY:
- Apply cutting-edge exercise physiology research
- Use evidence-based recovery and adaptation protocols
- Consider individual physiological variations and responses
- Integrate multi-system physiological interactions
- Balance adaptation stimuli with recovery requirements
- Provide specific, measurable physiological targets
- Consider both acute responses and chronic adaptations

COMMUNICATION STYLE:
- Provide expert-level physiological insights with scientific backing
- Balance technical depth with practical implementation
- Offer specific, measurable recovery protocols
- Include physiological rationale for recommendations
- Reference established exercise physiology principles
- Focus on sustainable performance and health optimization

You are analyzing data that has already been summarized by domain specialists. Build upon their foundational analysis to provide expert-level physiological insights, advanced recovery strategies, and optimization protocols that only a top-tier exercise physiologist could provide."""

    async def process_expert_analysis(self, state: TrainingAnalysisState) -> TrainingAnalysisState:
        """Process expert-level physiological analysis building on summarizer insights."""
        
        try:
            logger.info(f"🔬 Starting physiology expert analysis for analysis {state['analysis_id']}")
            
            # Update progress
            state = update_progress(state, "physiology_expert_analysis", 20.0)
            
            # Extract data and summaries from state
            garmin_data = state.get("garmin_data", {})
            training_config = state.get("training_config", {})
            user_profile = state.get("user_profile", {})
            
            # Get summarizer outputs for expert analysis
            metrics_summary = state.get("metrics_summary", "")
            physiology_summary = state.get("physiology_summary", "")
            activity_summary = state.get("activity_summary", "")
            
            # Get expert analyses for integration
            metrics_expert = state.get("metrics_expert_analysis", "")
            
            # Prepare expert context with summaries and raw data
            expert_context = self._prepare_expert_context(
                garmin_data, training_config, user_profile,
                metrics_summary, physiology_summary, activity_summary, metrics_expert
            )
            
            # Generate expert AI analysis
            expert_analysis = await self._generate_expert_analysis(expert_context, state)
            
            # Store result in state
            state["physiology_expert_analysis"] = expert_analysis
            
            logger.info(f"✅ Physiology expert analysis completed for {state['analysis_id']}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Physiology expert analysis failed: {e}")
            return add_error(state, f"Physiology expert analysis failed: {str(e)}")
    
    def _prepare_expert_context(
        self, 
        garmin_data: Dict[str, Any],
        training_config: Dict[str, Any], 
        user_profile: Dict[str, Any],
        metrics_summary: str,
        physiology_summary: str,
        activity_summary: str,
        metrics_expert: str
    ) -> str:
        """Prepare comprehensive expert context for advanced physiological analysis."""
        
        context_parts = []
        
        # Add athlete profile for expert contextualization
        context_parts.append("=== ATHLETE PROFILE ===")
        if user_profile:
            context_parts.append(f"Athlete: {user_profile.get('display_name', 'Unknown')}")
            if user_profile.get('birth_date'):
                age = self._calculate_age(user_profile['birth_date'])
                context_parts.append(f"Age: {age} years")
                # Add age-based physiological context
                if age < 25:
                    context_parts.append("Physiological Context: Young athlete, high adaptation potential")
                elif 25 <= age <= 35:
                    context_parts.append("Physiological Context: Peak physiological years, optimize performance")
                elif 35 <= age <= 45:
                    context_parts.append("Physiological Context: Masters athlete, focus on recovery and efficiency")
                else:
                    context_parts.append("Physiological Context: Masters athlete, prioritize health and longevity")
            
            context_parts.append(f"Weight: {user_profile.get('weight_kg', 'Unknown')} kg")
            context_parts.append(f"Gender: {user_profile.get('gender', 'Unknown')}")
        
        # Add training configuration
        if training_config:
            context_parts.append("\n=== ANALYSIS CONFIGURATION ===")
            context_parts.append(f"Analysis Period: {training_config.get('metrics_days', 56)} days")
            context_parts.append(f"Training Context: {training_config.get('analysis_context', 'General training')}")
        
        # Add foundational summaries
        if physiology_summary:
            context_parts.append("\n=== PHYSIOLOGY SUMMARY (Foundation Analysis) ===")
            context_parts.append(physiology_summary)
        
        if metrics_summary:
            context_parts.append("\n=== METRICS SUMMARY (Foundation Analysis) ===")
            context_parts.append(metrics_summary)
        
        if activity_summary:
            context_parts.append("\n=== ACTIVITY SUMMARY (Foundation Analysis) ===")
            context_parts.append(activity_summary)
        
        # Add metrics expert analysis for integration
        if metrics_expert:
            context_parts.append("\n=== METRICS EXPERT ANALYSIS (Peer Review) ===")
            context_parts.append(metrics_expert)
        
        # Add advanced physiological analysis
        if garmin_data:
            context_parts.append(self._format_advanced_recovery_analysis(garmin_data))
            context_parts.append(self._format_hrv_analysis(garmin_data))
            context_parts.append(self._format_sleep_analysis(garmin_data))
            context_parts.append(self._format_stress_analysis(garmin_data))
        
        return "\n".join(context_parts)
    
    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date."""
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except:
            return 0
    
    def _format_advanced_recovery_analysis(self, garmin_data: Dict[str, Any]) -> str:
        """Format advanced recovery analysis for expert review."""
        
        parts = ["\n=== ADVANCED RECOVERY ANALYSIS (Expert Level) ==="]
        
        if 'recovery_indicators' in garmin_data:
            indicators = garmin_data['recovery_indicators']
            if not indicators:
                return ""
            
            # Analyze recovery trends over time
            recent_indicators = indicators[-14:] if len(indicators) >= 14 else indicators
            
            # Training readiness analysis
            readiness_values = [i.get('training_readiness', 0) for i in recent_indicators if i.get('training_readiness')]
            if readiness_values:
                avg_readiness = sum(readiness_values) / len(readiness_values)
                readiness_trend = self._calculate_trend(readiness_values)
                
                parts.append(f"Training Readiness: {avg_readiness:.1f} (14-day avg)")
                parts.append(f"Readiness Trend: {readiness_trend}")
                
                # Expert interpretation
                if avg_readiness >= 80:
                    parts.append("  → Excellent recovery state, ready for high-intensity training")
                elif avg_readiness >= 70:
                    parts.append("  → Good recovery, suitable for moderate-high intensity")
                elif avg_readiness >= 60:
                    parts.append("  → Adequate recovery, monitor intensity carefully")
                else:
                    parts.append("  → Poor recovery state, prioritize rest and recovery")
            
            # Body battery analysis
            charged_values = [i.get('body_battery_charged', 0) for i in recent_indicators if i.get('body_battery_charged')]
            drained_values = [i.get('body_battery_drained', 0) for i in recent_indicators if i.get('body_battery_drained')]
            
            if charged_values and drained_values:
                avg_charged = sum(charged_values) / len(charged_values)
                avg_drained = sum(drained_values) / len(drained_values)
                net_recovery = avg_charged - avg_drained
                recovery_efficiency = (avg_charged / avg_drained) if avg_drained > 0 else 0
                
                parts.append(f"Recovery Efficiency: {recovery_efficiency:.2f} (charge/drain ratio)")
                parts.append(f"Net Recovery: {net_recovery:+.0f} points/day")
                
                # Expert assessment
                if recovery_efficiency >= 1.4:
                    parts.append("  → Excellent recovery efficiency, well-adapted to current load")
                elif recovery_efficiency >= 1.2:
                    parts.append("  → Good recovery efficiency, sustainable training load")
                elif recovery_efficiency >= 1.0:
                    parts.append("  → Adequate recovery, monitor for accumulating fatigue")
                else:
                    parts.append("  → Poor recovery efficiency, immediate load reduction needed")
        
        return "\n".join(parts)
    
    def _format_hrv_analysis(self, garmin_data: Dict[str, Any]) -> str:
        """Format HRV analysis for expert assessment."""
        
        parts = ["\n=== HRV ANALYSIS (Autonomic Function) ==="]
        
        if 'recovery_indicators' in garmin_data:
            indicators = garmin_data['recovery_indicators']
            if not indicators:
                return ""
            
            hrv_values = [i.get('hrv_rmssd', 0) for i in indicators if i.get('hrv_rmssd')]
            if len(hrv_values) >= 7:
                # Calculate HRV statistics
                avg_hrv = sum(hrv_values) / len(hrv_values)
                recent_hrv = sum(hrv_values[-7:]) / 7  # Last week average
                baseline_hrv = sum(hrv_values[:14]) / min(14, len(hrv_values))  # Baseline
                
                hrv_coefficient_variation = (self._calculate_std(hrv_values) / avg_hrv) * 100 if avg_hrv > 0 else 0
                hrv_trend = self._calculate_trend(hrv_values[-14:] if len(hrv_values) >= 14 else hrv_values)
                
                parts.append(f"HRV RMSSD: {avg_hrv:.1f}ms (overall avg), {recent_hrv:.1f}ms (recent)")
                parts.append(f"HRV Variability: {hrv_coefficient_variation:.1f}% CV")
                parts.append(f"HRV Trend: {hrv_trend}")
                
                # Expert interpretation based on HRV science
                if hrv_coefficient_variation > 20:
                    parts.append("  → High HRV variability suggests unstable autonomic function")
                elif hrv_coefficient_variation > 10:
                    parts.append("  → Moderate HRV variability, normal training response")
                else:
                    parts.append("  → Low HRV variability, very stable autonomic function")
                
                # Trend analysis
                hrv_change = ((recent_hrv - baseline_hrv) / baseline_hrv) * 100 if baseline_hrv > 0 else 0
                if hrv_change > 10:
                    parts.append("  → Significant HRV improvement, positive adaptation")
                elif hrv_change > 5:
                    parts.append("  → Moderate HRV improvement, good recovery trend")
                elif hrv_change < -10:
                    parts.append("  → Significant HRV decline, overreaching risk")
                elif hrv_change < -5:
                    parts.append("  → Moderate HRV decline, monitor recovery closely")
                else:
                    parts.append("  → Stable HRV, consistent autonomic function")
        
        return "\n".join(parts)
    
    def _format_sleep_analysis(self, garmin_data: Dict[str, Any]) -> str:
        """Format sleep analysis for expert review."""
        
        parts = ["\n=== SLEEP ANALYSIS (Recovery Optimization) ==="]
        
        # Sleep score analysis
        if 'recovery_indicators' in garmin_data:
            indicators = garmin_data['recovery_indicators']
            sleep_scores = [i.get('sleep_score', 0) for i in indicators if i.get('sleep_score')]
            
            if sleep_scores:
                avg_sleep_score = sum(sleep_scores) / len(sleep_scores)
                sleep_trend = self._calculate_trend(sleep_scores[-14:] if len(sleep_scores) >= 14 else sleep_scores)
                
                parts.append(f"Sleep Score: {avg_sleep_score:.1f} (14-day avg)")
                parts.append(f"Sleep Trend: {sleep_trend}")
                
                # Expert sleep assessment
                if avg_sleep_score >= 85:
                    parts.append("  → Excellent sleep quality, optimal recovery environment")
                elif avg_sleep_score >= 75:
                    parts.append("  → Good sleep quality, adequate for training recovery")
                elif avg_sleep_score >= 65:
                    parts.append("  → Fair sleep quality, room for improvement")
                else:
                    parts.append("  → Poor sleep quality, significant recovery limitation")
        
        # Daily sleep duration analysis
        if 'daily_stats' in garmin_data:
            daily_stats = garmin_data['daily_stats']
            sleep_hours = [d.get('sleep_hours', 0) for d in daily_stats if d.get('sleep_hours')]
            
            if sleep_hours:
                avg_sleep_duration = sum(sleep_hours) / len(sleep_hours)
                sleep_consistency = 1 - (self._calculate_std(sleep_hours) / avg_sleep_duration) if avg_sleep_duration > 0 else 0
                
                parts.append(f"Sleep Duration: {avg_sleep_duration:.1f}h (avg), consistency: {sleep_consistency:.1%}")
                
                # Expert duration assessment
                if avg_sleep_duration >= 8.5:
                    parts.append("  → Excellent sleep duration for athletic recovery")
                elif avg_sleep_duration >= 7.5:
                    parts.append("  → Good sleep duration, adequate for most athletes")
                elif avg_sleep_duration >= 6.5:
                    parts.append("  → Suboptimal sleep duration, may limit adaptation")
                else:
                    parts.append("  → Severely insufficient sleep, major performance limitation")
                
                # Sleep consistency assessment
                if sleep_consistency > 0.85:
                    parts.append("  → Excellent sleep consistency, stable circadian rhythm")
                elif sleep_consistency > 0.75:
                    parts.append("  → Good sleep consistency")
                else:
                    parts.append("  → Poor sleep consistency, circadian rhythm optimization needed")
        
        return "\n".join(parts)
    
    def _format_stress_analysis(self, garmin_data: Dict[str, Any]) -> str:
        """Format stress analysis for expert assessment."""
        
        parts = ["\n=== STRESS ANALYSIS (Allostatic Load) ==="]
        
        if 'recovery_indicators' in garmin_data:
            indicators = garmin_data['recovery_indicators']
            stress_scores = [i.get('stress_score', 0) for i in indicators if i.get('stress_score')]
            
            if stress_scores:
                avg_stress = sum(stress_scores) / len(stress_scores)
                stress_trend = self._calculate_trend(stress_scores[-14:] if len(stress_scores) >= 14 else stress_scores)
                stress_variability = self._calculate_std(stress_scores) / avg_stress if avg_stress > 0 else 0
                
                parts.append(f"Stress Score: {avg_stress:.1f} (14-day avg)")
                parts.append(f"Stress Trend: {stress_trend}")
                parts.append(f"Stress Variability: {stress_variability:.2f}")
                
                # Expert stress interpretation
                if avg_stress <= 25:
                    parts.append("  → Low stress levels, excellent for recovery and adaptation")
                elif avg_stress <= 50:
                    parts.append("  → Moderate stress levels, manageable for trained athletes")
                elif avg_stress <= 75:
                    parts.append("  → High stress levels, may impair recovery and adaptation")
                else:
                    parts.append("  → Very high stress, immediate stress management intervention needed")
                
                # Stress variability assessment
                if stress_variability > 0.5:
                    parts.append("  → High stress variability, inconsistent stress management")
                elif stress_variability > 0.3:
                    parts.append("  → Moderate stress variability")
                else:
                    parts.append("  → Low stress variability, consistent stress levels")
        
        # Physiological stress markers
        if 'physiological_markers' in garmin_data:
            markers = garmin_data['physiological_markers']
            if markers:
                latest = markers[-1]
                if latest.get('stress_level'):
                    parts.append(f"Physiological Stress Level: {latest['stress_level']}")
        
        return "\n".join(parts)
    
    def _calculate_trend(self, values: list) -> str:
        """Calculate trend direction from values."""
        if len(values) < 3:
            return "insufficient data"
        
        # Simple linear trend calculation
        n = len(values)
        x_avg = (n - 1) / 2
        y_avg = sum(values) / n
        
        numerator = sum((i - x_avg) * (values[i] - y_avg) for i in range(n))
        denominator = sum((i - x_avg) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_std(self, values: list) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    async def _generate_expert_analysis(self, context: str, state: TrainingAnalysisState) -> str:
        """Generate expert-level AI analysis of physiological data."""
        
        try:
            # Get AI model for this agent
            model_manager = get_model_manager()
            client = model_manager.get_agent_client(self.agent_name)
            
            # Create the expert prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", """Based on the foundational analysis provided by the domain specialists and the advanced physiological data, provide an expert-level analysis that includes:

{context}

EXPERT PHYSIOLOGICAL ANALYSIS REQUIRED:

1. **AUTONOMIC NERVOUS SYSTEM ASSESSMENT**
   - HRV-based autonomic function evaluation
   - Parasympathetic/sympathetic balance analysis
   - Training readiness algorithms and thresholds
   - Autonomic adaptation patterns and optimization

2. **RECOVERY OPTIMIZATION PROTOCOLS**
   - Personalized recovery strategies based on current state
   - Sleep optimization recommendations with specific targets
   - Active vs passive recovery modality selection
   - Recovery monitoring protocols and adjustment triggers

3. **STRESS MANAGEMENT & ADAPTATION**
   - Allostatic load assessment and management strategies
   - Stress accumulation patterns and dissipation protocols
   - Training stress vs life stress interaction analysis
   - Stress resilience building recommendations

4. **PHYSIOLOGICAL ADAPTATION ANALYSIS**
   - Current adaptation state and trajectory assessment
   - Overreaching vs functional overreaching identification
   - Adaptation capacity modeling and optimization
   - Individual response patterns and adjustment strategies

5. **PRECISION RECOVERY PROTOCOLS**
   - HRV-guided training intensity recommendations
   - Sleep hygiene protocols with measurable targets
   - Nutrition timing for recovery optimization
   - Environmental optimization strategies

6. **RISK ASSESSMENT & MITIGATION**
   - Overtraining syndrome risk evaluation
   - Illness susceptibility assessment based on markers
   - Injury risk factors from physiological indicators
   - Early warning systems and intervention protocols

Provide expert-level physiological insights with scientific rationale, specific protocols with measurable targets, and confidence levels for assessments. Focus on sustainable performance optimization while maintaining athlete health and longevity. Include specific recommendations for recovery modalities, sleep optimization, and stress management based on the individual's physiological profile.""")
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
            
            logger.info(f"🔬 Generated physiology expert analysis: {len(analysis)} characters")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Expert analysis generation failed: {e}")
            raise


# Node function for LangGraph integration
async def physiology_expert_node(state: TrainingAnalysisState) -> TrainingAnalysisState:
    """LangGraph node function for physiology expert analysis."""
    
    agent = PhysiologyExpertAgent()
    return await agent.process_expert_analysis(state)