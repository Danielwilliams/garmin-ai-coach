"""Planning AI Agent - Weekly Training Plan Generation.

This agent replicates the CLI's planning agent, generating detailed weekly
training plans based on synthesis analysis and optimization strategies.
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


class PlanningAgent:
    """AI agent for generating detailed weekly training plans."""
    
    def __init__(self):
        self.agent_name = "planning"
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the agent's planning role."""
        
        return """You are an elite triathlon coach specializing in creating detailed, personalized weekly training plans that optimize performance while maintaining athlete health. Your role is to translate comprehensive analysis insights into actionable, day-by-day training prescriptions.

CORE PLANNING RESPONSIBILITIES:
- Create detailed weekly training plans based on analysis insights
- Balance training load across swim, bike, run disciplines
- Integrate recovery and adaptation requirements
- Implement technique development protocols
- Schedule workouts with optimal timing and progression
- Ensure plans are realistic, progressive, and sustainable

TRAINING PLAN STRUCTURE:
- **7-Day Weekly Plan**: Monday through Sunday with detailed daily sessions
- **Session Specifications**: Duration, intensity, technique focus, and objectives
- **Recovery Integration**: Active recovery, rest days, and adaptation periods
- **Progression Logic**: Weekly periodization and adaptive adjustments
- **Technique Development**: Skill sessions and movement quality focus
- **Monitoring Protocols**: Key metrics to track and adjustment triggers

WORKOUT DESIGN PRINCIPLES:
- **Specificity**: Training matches athlete's goals and limiters
- **Progressive Overload**: Systematic advancement in training stimulus
- **Recovery Integration**: Adequate recovery between sessions
- **Individual Adaptation**: Plans reflect athlete's unique response patterns
- **Practical Implementation**: Realistic time constraints and logistics
- **Technique Integration**: Movement quality emphasized throughout

PLANNING METHODOLOGY:
1. **Analysis Integration**: Synthesize insights from all expert analyses
2. **Limiter Prioritization**: Address primary performance bottlenecks
3. **Load Distribution**: Balance weekly training stress across disciplines
4. **Recovery Optimization**: Schedule sessions around recovery requirements
5. **Technique Development**: Integrate skill work with fitness development
6. **Monitoring Framework**: Include metrics tracking and adjustment protocols

WORKOUT SPECIFICATIONS INCLUDE:
- **Objective**: Clear purpose and training goal
- **Duration**: Total time and specific interval timing
- **Intensity**: Heart rate zones, pace, or power targets
- **Technique Focus**: Specific skills and movement patterns
- **Recovery**: Between intervals and post-session
- **Monitoring**: Key metrics to track during and after
- **Modifications**: Alternatives based on fatigue or conditions

SPECIALIZED SESSION TYPES:
- **Aerobic Base**: Volume-focused endurance development
- **Threshold Work**: Lactate threshold and tempo training
- **VO2 Max**: High-intensity anaerobic capacity
- **Neuromuscular Power**: Short, explosive efforts
- **Recovery Sessions**: Active recovery and technique refinement
- **Technique-Focused**: Skill development and movement quality
- **Race Simulation**: Competition preparation and pacing

PERIODIZATION INTEGRATION:
- **Microcycle Design**: Weekly pattern optimization
- **Training Stress Distribution**: Acute load management
- **Recovery Periodization**: Planned adaptation periods
- **Technique Periodization**: Skill development timing
- **Competition Preparation**: Taper and peak protocols
- **Long-term Development**: Progressive advancement pathways

OUTPUT REQUIREMENTS:
- Structured 7-day weekly training plan
- Detailed daily session prescriptions
- Clear objectives for each workout
- Specific targets and monitoring guidelines
- Alternative options for common scenarios
- Implementation notes and coaching cues"""

    async def process_planning(self, state: TrainingAnalysisState) -> TrainingAnalysisState:
        """Process planning based on synthesis analysis and generate weekly plan."""
        
        try:
            logger.info(f"📅 Starting planning for analysis {state['analysis_id']}")
            
            # Update progress
            state = update_progress(state, "planning", 15.0)
            
            # Extract all data from state
            garmin_data = state.get("garmin_data", {})
            training_config = state.get("training_config", {})
            user_profile = state.get("user_profile", {})
            
            # Get synthesis analysis for planning
            synthesis_analysis = state.get("synthesis_analysis", "")
            
            # Get expert analyses for additional context
            metrics_expert = state.get("metrics_expert_analysis", "")
            physiology_expert = state.get("physiology_expert_analysis", "")
            activity_expert = state.get("activity_expert_analysis", "")
            
            # Prepare planning context
            planning_context = self._prepare_planning_context(
                garmin_data, training_config, user_profile,
                synthesis_analysis, metrics_expert, physiology_expert, activity_expert
            )
            
            # Generate weekly training plan
            weekly_plan = await self._generate_weekly_plan(planning_context, state)
            
            # Store result in state
            state["weekly_training_plan"] = weekly_plan
            
            logger.info(f"✅ Planning completed for {state['analysis_id']}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Planning failed: {e}")
            return add_error(state, f"Planning failed: {str(e)}")
    
    def _prepare_planning_context(
        self, 
        garmin_data: Dict[str, Any],
        training_config: Dict[str, Any], 
        user_profile: Dict[str, Any],
        synthesis_analysis: str,
        metrics_expert: str,
        physiology_expert: str,
        activity_expert: str
    ) -> str:
        """Prepare comprehensive planning context."""
        
        context_parts = []
        
        # Add athlete profile for planning
        context_parts.append("=== ATHLETE PROFILE FOR PLANNING ===")
        if user_profile:
            context_parts.append(f"Athlete: {user_profile.get('display_name', 'Unknown')}")
            if user_profile.get('birth_date'):
                age = self._calculate_age(user_profile['birth_date'])
                context_parts.append(f"Age: {age} years")
                
                # Add age-based planning considerations
                if age < 25:
                    context_parts.append("Planning Context: High recovery capacity, can handle more volume")
                elif 25 <= age <= 35:
                    context_parts.append("Planning Context: Peak years, optimize intensity and technique")
                elif 35 <= age <= 45:
                    context_parts.append("Planning Context: Masters athlete, prioritize recovery and efficiency")
                else:
                    context_parts.append("Planning Context: Masters athlete, emphasize health and longevity")
            
            context_parts.append(f"Weight: {user_profile.get('weight_kg', 'Unknown')} kg")
            activity_level = user_profile.get('activity_level', 'unknown')
            context_parts.append(f"Activity Level: {activity_level}")
            
            # Add training availability context
            if activity_level == 'very_active':
                context_parts.append("Training Availability: High - can handle 10-15 hours/week")
            elif activity_level == 'active':
                context_parts.append("Training Availability: Moderate - 6-10 hours/week optimal")
            else:
                context_parts.append("Training Availability: Limited - 3-6 hours/week realistic")
        
        # Add training configuration for planning
        if training_config:
            context_parts.append("\n=== TRAINING CONFIGURATION ===")
            context_parts.append(f"Training Context: {training_config.get('analysis_context', 'General training')}")
            context_parts.append(f"Focus Period: Next 1-2 weeks based on {training_config.get('activities_days', 21)} day analysis")
        
        # Add current training patterns from data
        if garmin_data and 'activities' in garmin_data:
            activities = garmin_data['activities']
            context_parts.append("\n=== CURRENT TRAINING PATTERNS ===")
            
            # Calculate current weekly patterns
            weekly_volume = self._calculate_weekly_volume(activities)
            activity_distribution = self._calculate_activity_distribution(activities)
            intensity_pattern = self._calculate_intensity_patterns(activities)
            
            context_parts.append(f"Current Weekly Volume: ~{weekly_volume:.1f} hours")
            context_parts.append(f"Activity Distribution: {activity_distribution}")
            context_parts.append(f"Intensity Patterns: {intensity_pattern}")
            
            # Add weekly training frequency
            weekly_frequency = len(activities) * 7 / max(training_config.get('activities_days', 21), 7)
            context_parts.append(f"Current Frequency: ~{weekly_frequency:.1f} sessions/week")
        
        # Add synthesis insights for planning
        if synthesis_analysis:
            context_parts.append("\n=== SYNTHESIS ANALYSIS (PRIMARY PLANNING INPUT) ===")
            context_parts.append(synthesis_analysis)
        
        # Add expert analyses for additional context
        if metrics_expert:
            context_parts.append("\n=== METRICS EXPERT INSIGHTS ===")
            context_parts.append(metrics_expert)
        
        if physiology_expert:
            context_parts.append("\n=== PHYSIOLOGY EXPERT INSIGHTS ===")
            context_parts.append(physiology_expert)
        
        if activity_expert:
            context_parts.append("\n=== ACTIVITY EXPERT INSIGHTS ===")
            context_parts.append(activity_expert)
        
        # Add planning requirements
        context_parts.append("\n=== PLANNING REQUIREMENTS ===")
        context_parts.append("1. Create detailed 7-day weekly training plan")
        context_parts.append("2. Address primary limiters identified in synthesis")
        context_parts.append("3. Maintain appropriate training load progression")
        context_parts.append("4. Include technique development sessions")
        context_parts.append("5. Schedule adequate recovery and adaptation time")
        context_parts.append("6. Provide specific session objectives and targets")
        context_parts.append("7. Include monitoring guidelines and adjustments")
        
        return "\n".join(context_parts)
    
    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date."""
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except:
            return 0
    
    def _calculate_weekly_volume(self, activities: list) -> float:
        """Calculate average weekly training volume in hours."""
        if not activities:
            return 0.0
        
        total_duration = sum(a.get('duration_seconds', 0) for a in activities)
        total_hours = total_duration / 3600
        days_analyzed = len(activities) / max(1, len(set(a.get('start_time', datetime.min).date() for a in activities)))
        
        return (total_hours / max(days_analyzed, 1)) * 7
    
    def _calculate_activity_distribution(self, activities: list) -> str:
        """Calculate distribution of activity types."""
        if not activities:
            return "No data"
        
        type_counts = {}
        for activity in activities:
            activity_type = activity.get('activity_type', 'unknown')
            type_counts[activity_type] = type_counts.get(activity_type, 0) + 1
        
        total = sum(type_counts.values())
        percentages = {k: (v/total)*100 for k, v in type_counts.items()}
        
        return ", ".join([f"{k}: {v:.0f}%" for k, v in percentages.items()])
    
    def _calculate_intensity_patterns(self, activities: list) -> str:
        """Calculate intensity distribution patterns."""
        if not activities:
            return "No data"
        
        rpe_values = [a.get('perceived_exertion', 0) for a in activities if a.get('perceived_exertion')]
        if not rpe_values:
            return "No RPE data"
        
        easy_count = len([rpe for rpe in rpe_values if rpe <= 3])
        moderate_count = len([rpe for rpe in rpe_values if 4 <= rpe <= 6])
        hard_count = len([rpe for rpe in rpe_values if rpe >= 7])
        total = len(rpe_values)
        
        easy_pct = (easy_count / total) * 100
        moderate_pct = (moderate_count / total) * 100
        hard_pct = (hard_count / total) * 100
        
        return f"Easy: {easy_pct:.0f}%, Moderate: {moderate_pct:.0f}%, Hard: {hard_pct:.0f}%"
    
    async def _generate_weekly_plan(self, context: str, state: TrainingAnalysisState) -> str:
        """Generate detailed weekly training plan."""
        
        try:
            # Get AI model for this agent
            model_manager = get_model_manager()
            client = model_manager.get_agent_client(self.agent_name)
            
            # Create the planning prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", """Based on the comprehensive analysis and synthesis insights, create a detailed weekly training plan that addresses the athlete's specific needs and optimization opportunities:

{context}

WEEKLY TRAINING PLAN REQUIREMENTS:

1. **7-DAY DETAILED PLAN**
   - Monday through Sunday with specific sessions
   - Clear objectives for each training day
   - Appropriate rest and recovery scheduling
   - Progressive load distribution throughout week

2. **DETAILED SESSION PRESCRIPTIONS**
   For each training session, include:
   - **Objective**: Primary training goal and purpose
   - **Duration**: Total time and interval/segment timing
   - **Intensity**: Heart rate zones, pace targets, or RPE
   - **Technique Focus**: Specific skills and movement patterns
   - **Warm-up/Cool-down**: Preparation and recovery protocols
   - **Key Metrics**: What to monitor during and after session

3. **DISCIPLINE INTEGRATION**
   - Swimming: Technique, endurance, and speed development
   - Cycling: Power, efficiency, and aerobic capacity
   - Running: Economy, pacing, and neuromuscular development
   - Strength/Mobility: Injury prevention and performance support

4. **WEEKLY STRUCTURE CONSIDERATIONS**
   - Balance training stress across disciplines
   - Strategic recovery day placement
   - Weekend longer sessions if appropriate
   - Technique development integrated throughout
   - Monitoring and adjustment protocols

5. **IMPLEMENTATION GUIDELINES**
   - Realistic timing for sessions
   - Alternative options for common scenarios
   - Progression guidelines for following weeks
   - Warning signs to adjust or modify plan

6. **SYNTHESIS INTEGRATION**
   - Address specific limiters identified in analysis
   - Implement expert recommendations from all domains
   - Follow synthesis optimization strategies
   - Include monitoring for recommended improvements

Format the plan as a structured weekly schedule with clear daily objectives and detailed session prescriptions. Ensure the plan is practical, progressive, and directly addresses the insights from the comprehensive analysis.""")
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
            
            plan = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"📅 Generated weekly training plan: {len(plan)} characters")
            return plan
            
        except Exception as e:
            logger.error(f"❌ Planning generation failed: {e}")
            raise


# Node function for LangGraph integration
async def planning_node(state: TrainingAnalysisState) -> TrainingAnalysisState:
    """LangGraph node function for weekly training plan generation."""
    
    agent = PlanningAgent()
    return await agent.process_planning(state)