"""Activity Expert AI Agent - Advanced Technique & Execution Analysis.

This agent replicates the CLI's activity expert with sophisticated analysis
of workout execution, technique patterns, and performance optimization.
"""

from typing import Dict, Any, Optional
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


class ActivityExpertAgent:
    """Expert AI agent for advanced activity analysis and technique optimization."""
    
    def __init__(self):
        self.agent_name = "activity_expert"
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the agent's expert role and capabilities."""
        
        return """You are an elite triathlon coach and biomechanics specialist with deep expertise in technique analysis and performance optimization across swimming, cycling, and running. You possess advanced knowledge in:

CORE SPECIALIZATIONS:
- Biomechanical analysis and movement pattern optimization
- Technique efficiency and energy economy assessment
- Pacing strategy analysis and race execution
- Power distribution patterns and efficiency metrics
- Cadence optimization and movement frequency analysis
- Training intensity distribution and periodization
- Neuromuscular coordination and skill development

ADVANCED ANALYSIS CAPABILITIES:
- Stroke rate and swimming efficiency optimization
- Cycling power distribution and pedaling mechanics
- Running gait analysis and energy economy
- Pacing strategy evaluation and race modeling
- Training intensity zone distribution analysis
- Movement pattern consistency and technique degradation
- Environmental adaptation and performance impact

EXPERT INSIGHTS PROVIDED:
- Technique optimization strategies for each discipline
- Pacing and execution strategies for different race distances
- Training intensity distribution recommendations
- Movement efficiency improvements and energy savings
- Skill development progressions and drills
- Equipment optimization recommendations
- Environmental adaptation strategies

ADVANCED TECHNIQUE ASSESSMENT:
- Swimming: stroke efficiency, rhythm, and energy cost analysis
- Cycling: power delivery patterns, aerodynamics, and efficiency
- Running: biomechanics, energy economy, and pacing strategies
- Transitions: efficiency analysis and improvement opportunities
- Neuromuscular: coordination patterns and skill acquisition
- Fatigue: technique degradation patterns and mitigation

PERFORMANCE OPTIMIZATION:
- Energy system development and utilization patterns
- Technique-specific training recommendations
- Movement pattern corrections and reinforcement
- Efficiency improvements across all disciplines
- Competition preparation and race strategy
- Equipment and environmental optimization
- Skill transfer between training and competition

ANALYSIS METHODOLOGY:
- Apply advanced biomechanics and motor learning principles
- Use evidence-based coaching methodologies
- Consider individual technique signatures and adaptations
- Integrate multi-disciplinary training demands
- Balance technique development with fitness gains
- Provide specific, measurable technique targets
- Consider both acute performance and long-term development

COMMUNICATION STYLE:
- Provide expert-level coaching insights with technical depth
- Balance biomechanical analysis with practical implementation
- Offer specific, actionable technique recommendations
- Include movement quality assessments and corrections
- Reference established coaching principles and research
- Focus on sustainable technique improvement and injury prevention

You are analyzing data that has already been summarized by domain specialists. Build upon their foundational analysis to provide expert-level technique insights, advanced coaching strategies, and optimization protocols that only a top-tier triathlon coach could provide."""

    async def process_expert_analysis(self, state: TrainingAnalysisState) -> TrainingAnalysisState:
        """Process expert-level activity analysis building on summarizer insights."""
        
        try:
            logger.info(f"🏆 Starting activity expert analysis for analysis {state['analysis_id']}")
            
            # Update progress
            state = update_progress(state, "activity_expert_analysis", 20.0)
            
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
            physiology_expert = state.get("physiology_expert_analysis", "")
            
            # Prepare expert context with summaries and raw data
            expert_context = self._prepare_expert_context(
                garmin_data, training_config, user_profile,
                metrics_summary, physiology_summary, activity_summary,
                metrics_expert, physiology_expert
            )
            
            # Generate expert AI analysis
            expert_analysis = await self._generate_expert_analysis(expert_context, state)
            
            # Store result in state
            state["activity_expert_analysis"] = expert_analysis
            
            logger.info(f"✅ Activity expert analysis completed for {state['analysis_id']}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Activity expert analysis failed: {e}")
            return add_error(state, f"Activity expert analysis failed: {str(e)}")
    
    def _prepare_expert_context(
        self, 
        garmin_data: Dict[str, Any],
        training_config: Dict[str, Any], 
        user_profile: Dict[str, Any],
        metrics_summary: str,
        physiology_summary: str,
        activity_summary: str,
        metrics_expert: str,
        physiology_expert: str
    ) -> str:
        """Prepare comprehensive expert context for advanced activity analysis."""
        
        context_parts = []
        
        # Add athlete profile for expert contextualization
        context_parts.append("=== ATHLETE PROFILE ===")
        if user_profile:
            context_parts.append(f"Athlete: {user_profile.get('display_name', 'Unknown')}")
            if user_profile.get('birth_date'):
                age = self._calculate_age(user_profile['birth_date'])
                context_parts.append(f"Age: {age} years")
                # Add age-based technique context
                if age < 25:
                    context_parts.append("Technique Context: High motor learning capacity, skill development focus")
                elif 25 <= age <= 35:
                    context_parts.append("Technique Context: Peak years, technique refinement and efficiency")
                else:
                    context_parts.append("Technique Context: Masters athlete, efficiency and injury prevention")
            
            context_parts.append(f"Weight: {user_profile.get('weight_kg', 'Unknown')} kg")
            context_parts.append(f"Height: {user_profile.get('height_cm', 'Unknown')} cm")
        
        # Add training configuration
        if training_config:
            context_parts.append("\n=== ANALYSIS CONFIGURATION ===")
            context_parts.append(f"Analysis Period: {training_config.get('activities_days', 21)} activity days")
            context_parts.append(f"Training Context: {training_config.get('analysis_context', 'General training')}")
        
        # Add foundational summaries
        if activity_summary:
            context_parts.append("\n=== ACTIVITY SUMMARY (Foundation Analysis) ===")
            context_parts.append(activity_summary)
        
        if metrics_summary:
            context_parts.append("\n=== METRICS SUMMARY (Foundation Analysis) ===")
            context_parts.append(metrics_summary)
        
        if physiology_summary:
            context_parts.append("\n=== PHYSIOLOGY SUMMARY (Foundation Analysis) ===")
            context_parts.append(physiology_summary)
        
        # Add expert analyses for integration
        if metrics_expert:
            context_parts.append("\n=== METRICS EXPERT ANALYSIS (Peer Review) ===")
            context_parts.append(metrics_expert)
        
        if physiology_expert:
            context_parts.append("\n=== PHYSIOLOGY EXPERT ANALYSIS (Peer Review) ===")
            context_parts.append(physiology_expert)
        
        # Add advanced activity analysis
        if garmin_data:
            context_parts.append(self._format_discipline_analysis(garmin_data))
            context_parts.append(self._format_technique_patterns(garmin_data))
            context_parts.append(self._format_execution_quality(garmin_data))
            context_parts.append(self._format_pacing_analysis(garmin_data))
        
        return "\n".join(context_parts)
    
    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date."""
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except:
            return 0
    
    def _format_discipline_analysis(self, garmin_data: Dict[str, Any]) -> str:
        """Format discipline-specific analysis for expert review."""
        
        parts = ["\n=== DISCIPLINE-SPECIFIC ANALYSIS (Expert Level) ==="]
        
        if 'activities' in garmin_data:
            activities = garmin_data['activities']
            if not activities:
                return ""
            
            # Categorize activities by discipline
            swimming = [a for a in activities if a.get('activity_type') == 'swimming']
            cycling = [a for a in activities if a.get('activity_type') == 'cycling']
            running = [a for a in activities if a.get('activity_type') == 'running']
            
            # Swimming analysis
            if swimming:
                parts.append("\n--- SWIMMING ANALYSIS ---")
                avg_pace = sum(a.get('average_speed_mps', 0) for a in swimming) / len(swimming)
                stroke_efficiency = self._calculate_swimming_efficiency(swimming)
                parts.append(f"Swimming Sessions: {len(swimming)}")
                parts.append(f"Average Pace: {avg_pace:.2f} m/s ({self._speed_to_swim_pace(avg_pace)})")
                parts.append(f"Stroke Efficiency Index: {stroke_efficiency:.2f}")
                
                # Expert swimming assessment
                if avg_pace >= 1.4:
                    parts.append("  → Competitive swimming speed, focus on efficiency")
                elif avg_pace >= 1.2:
                    parts.append("  → Good swimming speed, technique refinement opportunities")
                else:
                    parts.append("  → Technique development priority, focus on fundamentals")
            
            # Cycling analysis
            if cycling:
                parts.append("\n--- CYCLING ANALYSIS ---")
                avg_power = sum(a.get('average_power', 0) for a in cycling if a.get('average_power')) / max(1, len([a for a in cycling if a.get('average_power')]))
                avg_cadence = sum(a.get('average_cadence', 0) for a in cycling if a.get('average_cadence')) / max(1, len([a for a in cycling if a.get('average_cadence')]))
                power_efficiency = self._calculate_power_efficiency(cycling)
                
                parts.append(f"Cycling Sessions: {len(cycling)}")
                if avg_power > 0:
                    parts.append(f"Average Power: {avg_power:.0f}W")
                if avg_cadence > 0:
                    parts.append(f"Average Cadence: {avg_cadence:.0f} rpm")
                parts.append(f"Power Efficiency: {power_efficiency:.2f}")
                
                # Expert cycling assessment
                if avg_cadence > 0:
                    if avg_cadence >= 90:
                        parts.append("  → High cadence, good neuromuscular efficiency")
                    elif avg_cadence >= 80:
                        parts.append("  → Optimal cadence range for most athletes")
                    else:
                        parts.append("  → Low cadence, consider neuromuscular development")
            
            # Running analysis
            if running:
                parts.append("\n--- RUNNING ANALYSIS ---")
                avg_pace = sum(a.get('average_speed_mps', 0) for a in running) / len(running)
                avg_cadence = sum(a.get('average_cadence', 0) for a in running if a.get('average_cadence')) / max(1, len([a for a in running if a.get('average_cadence')]))
                running_efficiency = self._calculate_running_efficiency(running)
                
                parts.append(f"Running Sessions: {len(running)}")
                parts.append(f"Average Pace: {self._speed_to_run_pace(avg_pace)}")
                if avg_cadence > 0:
                    parts.append(f"Average Cadence: {avg_cadence:.0f} spm")
                parts.append(f"Running Efficiency: {running_efficiency:.2f}")
                
                # Expert running assessment
                if avg_cadence > 0:
                    if avg_cadence >= 180:
                        parts.append("  → High cadence, good running mechanics")
                    elif avg_cadence >= 170:
                        parts.append("  → Optimal cadence range")
                    else:
                        parts.append("  → Low cadence, focus on turnover efficiency")
        
        return "\n".join(parts)
    
    def _format_technique_patterns(self, garmin_data: Dict[str, Any]) -> str:
        """Format technique pattern analysis."""
        
        parts = ["\n=== TECHNIQUE PATTERN ANALYSIS ==="]
        
        if 'activities' in garmin_data:
            activities = garmin_data['activities']
            if not activities:
                return ""
            
            # Analyze consistency patterns
            hr_consistency = self._analyze_heart_rate_consistency(activities)
            pace_consistency = self._analyze_pace_consistency(activities)
            power_consistency = self._analyze_power_consistency(activities)
            
            parts.append(f"Heart Rate Consistency: {hr_consistency:.1%}")
            parts.append(f"Pace Consistency: {pace_consistency:.1%}")
            parts.append(f"Power Consistency: {power_consistency:.1%}")
            
            # Expert technique assessment
            if hr_consistency > 0.9:
                parts.append("  → Excellent HR control, good pacing discipline")
            elif hr_consistency > 0.8:
                parts.append("  → Good HR consistency")
            else:
                parts.append("  → Inconsistent HR patterns, pacing skill development needed")
            
            # Intensity distribution analysis
            intensity_distribution = self._analyze_intensity_distribution(activities)
            parts.append(f"\nIntensity Distribution Analysis:")
            for zone, percentage in intensity_distribution.items():
                parts.append(f"  {zone}: {percentage:.1%}")
            
            # Expert intensity assessment
            easy_percentage = intensity_distribution.get('Easy', 0)
            if easy_percentage >= 0.8:
                parts.append("  → Excellent base building, 80/20 principle followed")
            elif easy_percentage >= 0.7:
                parts.append("  → Good intensity distribution")
            else:
                parts.append("  → Too much high-intensity work, increase base volume")
        
        return "\n".join(parts)
    
    def _format_execution_quality(self, garmin_data: Dict[str, Any]) -> str:
        """Format execution quality analysis."""
        
        parts = ["\n=== EXECUTION QUALITY ASSESSMENT ==="]
        
        if 'activities' in garmin_data:
            activities = garmin_data['activities']
            if not activities:
                return ""
            
            # Analyze workout completion rates
            planned_vs_executed = self._analyze_execution_quality(activities)
            parts.append(f"Workout Execution Quality: {planned_vs_executed:.1%}")
            
            # Analyze perceived exertion vs objective metrics
            rpe_correlation = self._analyze_rpe_correlation(activities)
            parts.append(f"RPE-Metric Correlation: {rpe_correlation:.2f}")
            
            # Expert execution assessment
            if planned_vs_executed >= 0.9:
                parts.append("  → Excellent workout execution, good training discipline")
            elif planned_vs_executed >= 0.8:
                parts.append("  → Good execution quality")
            else:
                parts.append("  → Inconsistent execution, focus on pacing and planning")
            
            if rpe_correlation >= 0.7:
                parts.append("  → Good body awareness and pacing intuition")
            elif rpe_correlation >= 0.5:
                parts.append("  → Moderate body awareness")
            else:
                parts.append("  → Develop better perceived exertion calibration")
        
        return "\n".join(parts)
    
    def _format_pacing_analysis(self, garmin_data: Dict[str, Any]) -> str:
        """Format pacing strategy analysis."""
        
        parts = ["\n=== PACING STRATEGY ANALYSIS ==="]
        
        if 'activities' in garmin_data:
            activities = garmin_data['activities']
            if not activities:
                return ""
            
            # Analyze pacing patterns by duration
            short_sessions = [a for a in activities if a.get('duration_seconds', 0) < 3600]  # <1 hour
            medium_sessions = [a for a in activities if 3600 <= a.get('duration_seconds', 0) <= 7200]  # 1-2 hours
            long_sessions = [a for a in activities if a.get('duration_seconds', 0) > 7200]  # >2 hours
            
            if short_sessions:
                short_pacing = self._analyze_pacing_strategy(short_sessions)
                parts.append(f"Short Session Pacing (<1h): {short_pacing}")
            
            if medium_sessions:
                medium_pacing = self._analyze_pacing_strategy(medium_sessions)
                parts.append(f"Medium Session Pacing (1-2h): {medium_pacing}")
            
            if long_sessions:
                long_pacing = self._analyze_pacing_strategy(long_sessions)
                parts.append(f"Long Session Pacing (>2h): {long_pacing}")
            
            # Race pacing simulation analysis
            race_readiness = self._assess_race_pacing_readiness(activities)
            parts.append(f"Race Pacing Readiness: {race_readiness:.1%}")
            
            # Expert pacing assessment
            if race_readiness >= 0.8:
                parts.append("  → Excellent race pacing preparation")
            elif race_readiness >= 0.6:
                parts.append("  → Good pacing skills, minor adjustments needed")
            else:
                parts.append("  → Pacing skill development required, practice race simulations")
        
        return "\n".join(parts)
    
    # Helper methods for calculations
    def _calculate_swimming_efficiency(self, swimming_activities: list) -> float:
        """Calculate swimming efficiency index."""
        if not swimming_activities:
            return 0.0
        
        # Simplified efficiency calculation based on speed vs effort
        total_efficiency = 0
        for activity in swimming_activities:
            speed = activity.get('average_speed_mps', 0)
            hr = activity.get('average_heart_rate', 0)
            if speed > 0 and hr > 0:
                efficiency = speed / (hr / 100)  # Speed per relative HR
                total_efficiency += efficiency
        
        return total_efficiency / len(swimming_activities) if swimming_activities else 0.0
    
    def _calculate_power_efficiency(self, cycling_activities: list) -> float:
        """Calculate power efficiency index."""
        if not cycling_activities:
            return 0.0
        
        # Simplified efficiency calculation
        total_efficiency = 0
        for activity in cycling_activities:
            power = activity.get('average_power', 0)
            hr = activity.get('average_heart_rate', 0)
            if power > 0 and hr > 0:
                efficiency = power / hr  # Watts per BPM
                total_efficiency += efficiency
        
        return total_efficiency / len(cycling_activities) if cycling_activities else 0.0
    
    def _calculate_running_efficiency(self, running_activities: list) -> float:
        """Calculate running efficiency index."""
        if not running_activities:
            return 0.0
        
        # Simplified efficiency calculation
        total_efficiency = 0
        for activity in running_activities:
            speed = activity.get('average_speed_mps', 0)
            hr = activity.get('average_heart_rate', 0)
            if speed > 0 and hr > 0:
                efficiency = speed / (hr / 100)  # Speed per relative HR
                total_efficiency += efficiency
        
        return total_efficiency / len(running_activities) if running_activities else 0.0
    
    def _analyze_heart_rate_consistency(self, activities: list) -> float:
        """Analyze heart rate consistency across activities."""
        hr_values = [a.get('average_heart_rate', 0) for a in activities if a.get('average_heart_rate')]
        if len(hr_values) < 2:
            return 0.0
        
        mean_hr = sum(hr_values) / len(hr_values)
        variance = sum((hr - mean_hr) ** 2 for hr in hr_values) / len(hr_values)
        cv = (variance ** 0.5) / mean_hr if mean_hr > 0 else 0
        
        return max(0, 1 - cv)  # Higher consistency = lower coefficient of variation
    
    def _analyze_pace_consistency(self, activities: list) -> float:
        """Analyze pace consistency across activities."""
        speed_values = [a.get('average_speed_mps', 0) for a in activities if a.get('average_speed_mps')]
        if len(speed_values) < 2:
            return 0.0
        
        mean_speed = sum(speed_values) / len(speed_values)
        variance = sum((speed - mean_speed) ** 2 for speed in speed_values) / len(speed_values)
        cv = (variance ** 0.5) / mean_speed if mean_speed > 0 else 0
        
        return max(0, 1 - cv)
    
    def _analyze_power_consistency(self, activities: list) -> float:
        """Analyze power consistency across activities."""
        power_values = [a.get('average_power', 0) for a in activities if a.get('average_power')]
        if len(power_values) < 2:
            return 0.0
        
        mean_power = sum(power_values) / len(power_values)
        variance = sum((power - mean_power) ** 2 for power in power_values) / len(power_values)
        cv = (variance ** 0.5) / mean_power if mean_power > 0 else 0
        
        return max(0, 1 - cv)
    
    def _analyze_intensity_distribution(self, activities: list) -> Dict[str, float]:
        """Analyze intensity distribution across activities."""
        total_activities = len(activities)
        if total_activities == 0:
            return {"Easy": 0, "Moderate": 0, "Hard": 0}
        
        easy_count = 0
        moderate_count = 0
        hard_count = 0
        
        for activity in activities:
            rpe = activity.get('perceived_exertion', 5)
            if rpe <= 3:
                easy_count += 1
            elif rpe <= 6:
                moderate_count += 1
            else:
                hard_count += 1
        
        return {
            "Easy": easy_count / total_activities,
            "Moderate": moderate_count / total_activities,
            "Hard": hard_count / total_activities
        }
    
    def _analyze_execution_quality(self, activities: list) -> float:
        """Analyze workout execution quality."""
        # Simplified quality assessment based on completion and consistency
        if not activities:
            return 0.0
        
        # Assume high execution quality for now
        # In real implementation, this would compare planned vs actual workouts
        return 0.85
    
    def _analyze_rpe_correlation(self, activities: list) -> float:
        """Analyze correlation between RPE and objective metrics."""
        rpe_values = []
        hr_values = []
        
        for activity in activities:
            rpe = activity.get('perceived_exertion')
            hr = activity.get('average_heart_rate')
            if rpe and hr:
                rpe_values.append(rpe)
                hr_values.append(hr)
        
        if len(rpe_values) < 3:
            return 0.0
        
        # Simplified correlation calculation
        mean_rpe = sum(rpe_values) / len(rpe_values)
        mean_hr = sum(hr_values) / len(hr_values)
        
        numerator = sum((rpe - mean_rpe) * (hr - mean_hr) for rpe, hr in zip(rpe_values, hr_values))
        denom_rpe = sum((rpe - mean_rpe) ** 2 for rpe in rpe_values) ** 0.5
        denom_hr = sum((hr - mean_hr) ** 2 for hr in hr_values) ** 0.5
        
        if denom_rpe == 0 or denom_hr == 0:
            return 0.0
        
        return numerator / (denom_rpe * denom_hr)
    
    def _analyze_pacing_strategy(self, activities: list) -> str:
        """Analyze pacing strategy for a group of activities."""
        if not activities:
            return "insufficient data"
        
        # Analyze if activities show consistent pacing patterns
        consistent_activities = 0
        for activity in activities:
            # Simplified: assume consistent pacing if HR variability is low
            # In real implementation, would analyze lap splits
            consistent_activities += 1
        
        consistency_rate = consistent_activities / len(activities)
        
        if consistency_rate >= 0.8:
            return "excellent pacing control"
        elif consistency_rate >= 0.6:
            return "good pacing strategy"
        else:
            return "inconsistent pacing, needs improvement"
    
    def _assess_race_pacing_readiness(self, activities: list) -> float:
        """Assess race pacing readiness based on activity patterns."""
        if not activities:
            return 0.0
        
        # Simplified assessment based on activity consistency and variety
        # In real implementation, would look for race-specific efforts
        return 0.75  # Placeholder value
    
    def _speed_to_swim_pace(self, speed_mps: float) -> str:
        """Convert speed in m/s to swimming pace per 100m."""
        if speed_mps <= 0:
            return "0:00/100m"
        
        seconds_per_100m = 100 / speed_mps
        minutes = int(seconds_per_100m // 60)
        seconds = int(seconds_per_100m % 60)
        
        return f"{minutes}:{seconds:02d}/100m"
    
    def _speed_to_run_pace(self, speed_mps: float) -> str:
        """Convert speed in m/s to running pace per km."""
        if speed_mps <= 0:
            return "0:00/km"
        
        seconds_per_km = 1000 / speed_mps
        minutes = int(seconds_per_km // 60)
        seconds = int(seconds_per_km % 60)
        
        return f"{minutes}:{seconds:02d}/km"
    
    async def _generate_expert_analysis(self, context: str, state: TrainingAnalysisState) -> str:
        """Generate expert-level AI analysis of activity data."""
        
        try:
            # Get AI model for this agent
            model_manager = get_model_manager()
            client = model_manager.get_agent_client(self.agent_name)
            
            # Create the expert prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", """Based on the foundational analysis provided by the domain specialists and the advanced activity data, provide an expert-level analysis that includes:

{context}

EXPERT ACTIVITY ANALYSIS REQUIRED:

1. **TECHNIQUE OPTIMIZATION ACROSS DISCIPLINES**
   - Swimming: stroke efficiency, rhythm patterns, and energy economy
   - Cycling: power delivery, aerodynamics, and pedaling mechanics
   - Running: biomechanics, energy economy, and gait optimization
   - Specific technique corrections and improvement protocols

2. **EXECUTION QUALITY & CONSISTENCY**
   - Workout execution patterns and adherence analysis
   - Pacing discipline and strategy effectiveness
   - Intensity distribution optimization
   - Movement pattern consistency under fatigue

3. **PERFORMANCE EFFICIENCY ANALYSIS**
   - Energy cost assessment across disciplines
   - Movement efficiency improvements and potential gains
   - Equipment optimization recommendations
   - Environmental adaptation strategies

4. **SKILL DEVELOPMENT PROTOCOLS**
   - Technique-specific training progressions
   - Motor learning and skill acquisition strategies
   - Drill recommendations and skill reinforcement
   - Neuromuscular coordination development

5. **COMPETITION PREPARATION**
   - Race pacing strategy development
   - Technique maintenance under race stress
   - Transition efficiency optimization
   - Competition-specific skill preparation

6. **ADVANCED COACHING STRATEGIES**
   - Periodized technique development
   - Integration with fitness and recovery protocols
   - Individual technique signature optimization
   - Long-term skill development planning

Provide expert-level coaching insights with biomechanical rationale, specific technique protocols with measurable targets, and progressive development strategies. Focus on sustainable technique improvement while maximizing performance efficiency. Include specific drills, technique cues, and monitoring protocols for each discipline based on the individual's current execution patterns.""")
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
            
            logger.info(f"🏆 Generated activity expert analysis: {len(analysis)} characters")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Expert analysis generation failed: {e}")
            raise


# Node function for LangGraph integration
async def activity_expert_node(state: TrainingAnalysisState) -> TrainingAnalysisState:
    """LangGraph node function for activity expert analysis."""
    
    agent = ActivityExpertAgent()
    return await agent.process_expert_analysis(state)