"""Synthesis AI Agent - Integration & Comprehensive Analysis.

This agent replicates the CLI's synthesis agent, integrating all expert analyses
into cohesive recommendations and actionable insights.
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


class SynthesisAgent:
    """AI agent for synthesizing expert analyses into comprehensive recommendations."""
    
    def __init__(self):
        self.agent_name = "synthesis"
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the agent's synthesis role."""
        
        return """You are an elite triathlon coach and sports scientist with the unique ability to synthesize complex, multi-disciplinary analyses into coherent, actionable training strategies. Your role is to integrate insights from multiple expert domains and create unified recommendations that optimize performance while maintaining athlete health.

CORE SYNTHESIS RESPONSIBILITIES:
- Integrate metrics, physiology, and activity expert analyses into coherent strategies
- Identify synergies and conflicts between different expert recommendations
- Prioritize interventions based on impact potential and implementation feasibility
- Create holistic training strategies that balance all performance factors
- Translate complex scientific insights into practical, actionable plans
- Ensure recommendations are realistic, measurable, and progressive

EXPERT INTEGRATION METHODOLOGY:
- Analyze convergent insights from multiple expert domains
- Resolve conflicts between competing recommendations
- Identify primary limiting factors and optimization opportunities
- Prioritize interventions by impact magnitude and implementation timeline
- Create integrated protocols that address multiple performance factors
- Ensure recommendations are athlete-specific and context-appropriate

SYNTHESIS ANALYSIS FRAMEWORK:
1. **Cross-Domain Analysis**: Identify patterns and conflicts across expert analyses
2. **Priority Assessment**: Rank improvement opportunities by impact and feasibility
3. **Strategy Integration**: Develop unified approaches that address multiple factors
4. **Implementation Planning**: Create realistic, progressive development protocols
5. **Risk Assessment**: Identify potential conflicts or overload scenarios
6. **Monitoring Framework**: Establish metrics for tracking progress and adjustments

STRATEGIC RECOMMENDATIONS PROVIDED:
- Integrated training optimization strategies
- Periodization adjustments based on multi-factor analysis
- Recovery and adaptation optimization protocols
- Technique development priorities and timelines
- Performance bottleneck identification and solutions
- Risk mitigation strategies across all domains
- Progressive development pathways with measurable milestones

COMMUNICATION PRINCIPLES:
- Synthesize complex information into clear, actionable insights
- Provide specific, measurable, and time-bound recommendations
- Balance technical depth with practical implementation
- Address the athlete's complete performance ecosystem
- Include confidence levels and alternative approaches
- Focus on sustainable, long-term performance optimization

ANALYSIS INTEGRATION APPROACH:
You will receive expert analyses from three specialized domains:
1. Metrics Expert: Training load, performance trends, and optimization
2. Physiology Expert: Recovery, adaptation, and physiological optimization
3. Activity Expert: Technique, execution quality, and skill development

Your task is to synthesize these expert insights into a unified strategy that addresses the athlete's complete performance picture, identifying synergies, resolving conflicts, and creating integrated protocols that optimize all aspects of triathlon performance."""

    async def process_synthesis(self, state: TrainingAnalysisState) -> TrainingAnalysisState:
        """Process synthesis of all expert analyses into unified recommendations."""
        
        try:
            logger.info(f"🎯 Starting synthesis analysis for analysis {state['analysis_id']}")
            
            # Update progress
            state = update_progress(state, "synthesis", 25.0)
            
            # Extract all analyses from state
            garmin_data = state.get("garmin_data", {})
            training_config = state.get("training_config", {})
            user_profile = state.get("user_profile", {})
            
            # Get all expert analyses
            metrics_summary = state.get("metrics_summary", "")
            physiology_summary = state.get("physiology_summary", "")
            activity_summary = state.get("activity_summary", "")
            
            metrics_expert = state.get("metrics_expert_analysis", "")
            physiology_expert = state.get("physiology_expert_analysis", "")
            activity_expert = state.get("activity_expert_analysis", "")
            
            # Prepare synthesis context
            synthesis_context = self._prepare_synthesis_context(
                garmin_data, training_config, user_profile,
                metrics_summary, physiology_summary, activity_summary,
                metrics_expert, physiology_expert, activity_expert
            )
            
            # Generate synthesis analysis
            synthesis_analysis = await self._generate_synthesis_analysis(synthesis_context, state)
            
            # Store result in state
            state["synthesis_analysis"] = synthesis_analysis
            
            logger.info(f"✅ Synthesis analysis completed for {state['analysis_id']}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Synthesis analysis failed: {e}")
            return add_error(state, f"Synthesis analysis failed: {str(e)}")
    
    def _prepare_synthesis_context(
        self, 
        garmin_data: Dict[str, Any],
        training_config: Dict[str, Any], 
        user_profile: Dict[str, Any],
        metrics_summary: str,
        physiology_summary: str,
        activity_summary: str,
        metrics_expert: str,
        physiology_expert: str,
        activity_expert: str
    ) -> str:
        """Prepare comprehensive synthesis context."""
        
        context_parts = []
        
        # Add athlete profile for context
        context_parts.append("=== ATHLETE PROFILE ===")
        if user_profile:
            context_parts.append(f"Athlete: {user_profile.get('display_name', 'Unknown')}")
            if user_profile.get('birth_date'):
                age = self._calculate_age(user_profile['birth_date'])
                context_parts.append(f"Age: {age} years")
            context_parts.append(f"Weight: {user_profile.get('weight_kg', 'Unknown')} kg")
            context_parts.append(f"Activity Level: {user_profile.get('activity_level', 'Unknown')}")
        
        # Add training configuration
        if training_config:
            context_parts.append("\n=== TRAINING CONFIGURATION ===")
            context_parts.append(f"Analysis Period: {training_config.get('activities_days', 21)} activity days")
            context_parts.append(f"Training Context: {training_config.get('analysis_context', 'General training')}")
            context_parts.append(f"AI Mode: {training_config.get('ai_mode', 'development')}")
        
        # Add data summary for context
        if garmin_data:
            context_parts.append("\n=== DATA SUMMARY ===")
            total_activities = len(garmin_data.get('activities', []))
            context_parts.append(f"Total Activities Analyzed: {total_activities}")
            
            # Add data quality indicators
            has_hr_data = any(a.get('average_heart_rate') for a in garmin_data.get('activities', []))
            has_power_data = any(a.get('average_power') for a in garmin_data.get('activities', []))
            has_recovery_data = len(garmin_data.get('recovery_indicators', [])) > 0
            
            data_quality = []
            if has_hr_data:
                data_quality.append("Heart Rate")
            if has_power_data:
                data_quality.append("Power")
            if has_recovery_data:
                data_quality.append("Recovery Metrics")
            
            context_parts.append(f"Available Data Types: {', '.join(data_quality) if data_quality else 'Limited data'}")
        
        # Add foundational summaries
        context_parts.append("\n=== FOUNDATIONAL ANALYSES ===")
        
        if metrics_summary:
            context_parts.append("\n--- METRICS SUMMARY ---")
            context_parts.append(metrics_summary)
        
        if physiology_summary:
            context_parts.append("\n--- PHYSIOLOGY SUMMARY ---")
            context_parts.append(physiology_summary)
        
        if activity_summary:
            context_parts.append("\n--- ACTIVITY SUMMARY ---")
            context_parts.append(activity_summary)
        
        # Add expert analyses for synthesis
        context_parts.append("\n=== EXPERT ANALYSES FOR SYNTHESIS ===")
        
        if metrics_expert:
            context_parts.append("\n--- METRICS EXPERT ANALYSIS ---")
            context_parts.append(metrics_expert)
        
        if physiology_expert:
            context_parts.append("\n--- PHYSIOLOGY EXPERT ANALYSIS ---")
            context_parts.append(physiology_expert)
        
        if activity_expert:
            context_parts.append("\n--- ACTIVITY EXPERT ANALYSIS ---")
            context_parts.append(activity_expert)
        
        # Add synthesis framework
        context_parts.append("\n=== SYNTHESIS REQUIREMENTS ===")
        context_parts.append("1. Identify convergent insights and validate consistency")
        context_parts.append("2. Resolve conflicts between expert recommendations")
        context_parts.append("3. Prioritize interventions by impact and feasibility")
        context_parts.append("4. Create integrated optimization strategy")
        context_parts.append("5. Establish monitoring and adjustment protocols")
        
        return "\n".join(context_parts)
    
    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date."""
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except:
            return 0
    
    async def _generate_synthesis_analysis(self, context: str, state: TrainingAnalysisState) -> str:
        """Generate comprehensive synthesis analysis."""
        
        try:
            # Get AI model for this agent
            model_manager = get_model_manager()
            client = model_manager.get_agent_client(self.agent_name)
            
            # Create the synthesis prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", """Based on the expert analyses from metrics, physiology, and activity specialists, synthesize their insights into a comprehensive performance optimization strategy:

{context}

SYNTHESIS ANALYSIS REQUIRED:

1. **CROSS-DOMAIN INSIGHT INTEGRATION**
   - Identify convergent themes across all expert analyses
   - Highlight complementary recommendations that reinforce each other
   - Map relationships between training load, recovery, and technique factors
   - Assess consistency and validate expert agreement areas

2. **CONFLICT RESOLUTION & PRIORITIZATION**
   - Identify conflicts between expert recommendations
   - Resolve competing priorities with evidence-based rationale
   - Establish intervention hierarchy based on impact magnitude
   - Create timeline for implementation that avoids overload

3. **PRIMARY LIMITING FACTORS ANALYSIS**
   - Identify the top 3 performance limiters from integrated analysis
   - Assess which factors have highest improvement potential
   - Determine interdependencies between limiting factors
   - Establish which improvements unlock others

4. **INTEGRATED OPTIMIZATION STRATEGY**
   - Create unified training strategy addressing all expert domains
   - Develop periodization approach that optimizes load, recovery, and technique
   - Establish progressive development pathway with clear milestones
   - Ensure strategy is realistic and sustainable for the athlete

5. **IMPLEMENTATION FRAMEWORK**
   - Provide specific, actionable next steps with timelines
   - Create monitoring protocols to track multi-domain progress
   - Establish adjustment triggers and decision points
   - Include backup strategies for common implementation challenges

6. **RISK ASSESSMENT & MITIGATION**
   - Identify potential conflicts between recommendations
   - Assess overload risks from multiple simultaneous interventions
   - Provide early warning indicators and adjustment protocols
   - Create contingency plans for various response scenarios

7. **SUCCESS METRICS & MONITORING**
   - Define measurable outcomes for each optimization area
   - Create integrated dashboard of key performance indicators
   - Establish review cycles and adjustment protocols
   - Provide benchmarks for short, medium, and long-term progress

Synthesize the expert analyses into a cohesive, prioritized, and actionable strategy that optimizes the athlete's complete performance system. Focus on creating synergistic improvements while maintaining sustainable development and injury prevention. Provide confidence levels for recommendations and include alternative approaches where appropriate.""")
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
            
            logger.info(f"🎯 Generated synthesis analysis: {len(analysis)} characters")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Synthesis analysis generation failed: {e}")
            raise


# Node function for LangGraph integration
async def synthesis_node(state: TrainingAnalysisState) -> TrainingAnalysisState:
    """LangGraph node function for synthesis analysis."""
    
    agent = SynthesisAgent()
    return await agent.process_synthesis(state)