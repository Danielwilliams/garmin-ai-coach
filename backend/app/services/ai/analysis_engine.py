"""Analysis Engine - Main orchestrator for AI analysis system.

This is the primary interface for starting and managing training analysis,
replicating the exact functionality from the CLI application.
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from app.services.ai.model_config import initialize_model_manager, AIMode
from app.services.ai.langgraph.state.training_analysis_state import (
    initialize_analysis_state, 
    TrainingAnalysisState
)
from app.services.ai.langgraph.workflows.training_analysis_workflow import workflow_engine
from app.database.models.analysis import Analysis, AnalysisResult
from app.database.models.training_config import TrainingConfig
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID


class AnalysisEngine:
    """Main analysis engine that coordinates the entire AI analysis process."""
    
    def __init__(self):
        self.workflow = workflow_engine
        self._model_manager = None
    
    async def start_analysis(
        self,
        user_id: str,
        training_config_id: str,
        analysis_config: Dict[str, Any],
        db: AsyncSession
    ) -> str:
        """Start a new training analysis.
        
        Args:
            user_id: ID of the user requesting analysis
            training_config_id: ID of training configuration to use
            analysis_config: Analysis configuration parameters
            db: Database session
            
        Returns:
            analysis_id: Unique identifier for the started analysis
        """
        
        # Generate analysis ID
        analysis_id = str(uuid4())
        
        # Initialize model manager with AI mode
        ai_mode = AIMode(analysis_config.get("ai_mode", "development"))
        self._model_manager = initialize_model_manager(ai_mode)
        
        # Load training configuration from database
        training_config = await self._load_training_config(training_config_id, db)
        
        # Create initial analysis state with correct parameters
        # Merge training config data into analysis config for state initialization
        merged_config = {
            **analysis_config,
            "analysis_type": analysis_config.get("analysis_type", "full_analysis"),
            "ai_mode": training_config.get("ai_mode", analysis_config.get("ai_mode", "development")),
            "activities_days": training_config.get("activities_days", 21),
            "metrics_days": training_config.get("metrics_days", 56),
            "enable_plotting": training_config.get("enable_plotting", False),
            "hitl_enabled": training_config.get("hitl_enabled", False),
            "skip_synthesis": training_config.get("skip_synthesis", False),
        }
        
        initial_state = initialize_analysis_state(
            analysis_id=analysis_id,
            user_id=user_id,
            training_config_id=training_config_id,
            analysis_config=merged_config
        )
        
        # Add training config data to state
        initial_state["training_config"] = training_config
        initial_state["training_context"] = training_config.get("analysis_context")
        initial_state["planning_context"] = training_config.get("planning_context")
        
        # Create analysis record in database
        await self._create_analysis_record(initial_state, db)
        
        # Start workflow execution in background
        asyncio.create_task(self._execute_analysis_workflow(initial_state, db))
        
        return analysis_id
    
    async def _load_training_config(
        self, 
        training_config_id: str, 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Load training configuration from database."""
        
        try:
            # Load training config from database
            query = select(TrainingConfig).where(TrainingConfig.id == UUID(training_config_id))
            result = await db.execute(query)
            config = result.scalar_one_or_none()
            
            if not config:
                # Return default config if not found
                return {
                    "id": training_config_id,
                    "name": "Default Training Config",
                    "analysis_context": "General training analysis",
                    "planning_context": "Weekly training planning",
                    "activities_days": 21,
                    "metrics_days": 56,
                    "ai_mode": "development",
                    "enable_plotting": False,
                    "hitl_enabled": False,
                    "skip_synthesis": False
                }
            
            # Convert to dictionary including Garmin credentials
            return {
                "id": str(config.id),
                "name": config.name,
                "athlete_name": config.athlete_name,
                "athlete_email": config.athlete_email,
                "analysis_context": config.analysis_context or "General training analysis",
                "planning_context": config.planning_context or "Weekly training planning",
                "training_needs": config.training_needs,
                "session_constraints": config.session_constraints,
                "training_preferences": config.training_preferences,
                "activities_days": config.activities_days,
                "metrics_days": config.metrics_days,
                "ai_mode": config.ai_mode,
                "enable_plotting": config.enable_plotting,
                "hitl_enabled": config.hitl_enabled,
                "skip_synthesis": config.skip_synthesis,
                "garmin_email": config.garmin_email,
                "garmin_password_encrypted": config.garmin_password_encrypted,
                "garmin_is_connected": config.garmin_is_connected
            }
            
        except Exception as e:
            print(f"Error loading training config: {e}")
            # Return default config on error
            return {
                "id": training_config_id,
                "name": "Default Training Config",
                "analysis_context": "General training analysis",
                "activities_days": 21,
                "metrics_days": 56,
                "ai_mode": "development",
                "enable_plotting": False,
                "hitl_enabled": False,
                "skip_synthesis": False
            }
    
    async def _create_analysis_record(
        self, 
        state: TrainingAnalysisState, 
        db: AsyncSession
    ) -> None:
        """Create initial analysis record in database."""
        
        try:
            # Create Analysis model instance
            analysis = Analysis(
                id=UUID(state["analysis_id"]),
                user_id=UUID(state["user_id"]),
                training_config_id=UUID(state["training_config_id"]),
                status="running",
                analysis_type=state["analysis_type"],
                workflow_id=state["workflow_id"],
                progress_percentage=0,
                total_tokens=0,
                estimated_cost="$0.00",
                retry_count=0
            )
            
            db.add(analysis)
            await db.commit()
            await db.refresh(analysis)
            
            print(f"📊 Created analysis record: {analysis.id}")
            
        except Exception as e:
            print(f"❌ Failed to create analysis record: {e}")
            await db.rollback()
            raise
    
    async def _execute_analysis_workflow(
        self, 
        initial_state: TrainingAnalysisState,
        db: AsyncSession
    ) -> None:
        """Execute the complete analysis workflow in background."""
        
        try:
            print(f"🚀 Starting analysis workflow: {initial_state['analysis_id']}")
            
            # Execute the LangGraph workflow
            final_state = await self.workflow.execute_workflow(initial_state)
            
            # Save final results to database
            await self._save_analysis_results(final_state, db)
            
            print(f"✅ Analysis workflow completed: {final_state['analysis_id']}")
            
        except Exception as e:
            print(f"❌ Analysis workflow failed: {e}")
            
            # Update analysis status to failed
            await self._mark_analysis_failed(initial_state["analysis_id"], str(e), db)
    
    async def _save_analysis_results(
        self, 
        final_state: TrainingAnalysisState,
        db: AsyncSession
    ) -> None:
        """Save analysis results to database."""
        
        try:
            analysis_id = UUID(final_state["analysis_id"])
            
            # Calculate total tokens and cost
            total_tokens = 0
            total_cost = final_state.get("total_cost", 0.0)
            
            token_usage = final_state.get("token_usage", {})
            for agent_usage_list in token_usage.values():
                for usage in agent_usage_list:
                    if isinstance(usage, dict):
                        total_tokens += usage.get("total_tokens", 0)
                    else:
                        total_tokens += getattr(usage, "total_tokens", 0)
            
            # Update main analysis record
            progress = final_state.get("progress", {})
            
            update_stmt = (
                update(Analysis)
                .where(Analysis.id == analysis_id)
                .values(
                    status="completed" if final_state.get("workflow_complete") else "failed",
                    progress_percentage=int(progress.get("overall_percentage", 100)),
                    summary=final_state.get("synthesis_analysis"),
                    recommendations=self._extract_recommendations(final_state),
                    weekly_plan=final_state.get("weekly_training_plan"),
                    total_tokens=total_tokens,
                    estimated_cost=f"${total_cost:.2f}" if total_cost > 0 else "$0.00",
                    end_date=final_state.get("end_time"),
                    error_message=None if final_state.get("workflow_complete") else "Workflow failed"
                )
            )
            
            await db.execute(update_stmt)
            
            # Save individual analysis results
            await self._save_individual_results(final_state, db)
            
            await db.commit()
            
            print(f"💾 Saved analysis results for {analysis_id}")
            
        except Exception as e:
            print(f"❌ Failed to save analysis results: {e}")
            await db.rollback()
            raise
    
    async def _save_individual_results(
        self, 
        final_state: TrainingAnalysisState,
        db: AsyncSession
    ) -> None:
        """Save individual agent results as AnalysisResult records."""
        
        analysis_id = UUID(final_state["analysis_id"])
        
        # Save results from each agent
        result_mappings = [
            ("metrics_summary", "metrics_summarizer", "summary", "Metrics Analysis Summary"),
            ("physiology_summary", "physiology_summarizer", "summary", "Physiology Analysis Summary"), 
            ("activity_summary", "activity_summarizer", "summary", "Activity Analysis Summary"),
            ("metrics_expert_analysis", "metrics_expert", "expert_analysis", "Metrics Expert Analysis"),
            ("physiology_expert_analysis", "physiology_expert", "expert_analysis", "Physiology Expert Analysis"),
            ("activity_expert_analysis", "activity_expert", "expert_analysis", "Activity Expert Analysis"),
            ("synthesis_analysis", "synthesis", "synthesis", "Comprehensive Analysis Synthesis"),
            ("formatted_report", "formatting", "formatted_output", "Formatted Analysis Report"),
            ("weekly_training_plan", "planning", "training_plan", "Weekly Training Plan")
        ]
        
        for state_key, node_name, result_type, title in result_mappings:
            content = final_state.get(state_key)
            if content:
                # Get token usage for this agent
                agent_tokens = 0
                token_usage = final_state.get("token_usage", {}).get(node_name, [])
                for usage in token_usage:
                    if isinstance(usage, dict):
                        agent_tokens += usage.get("total_tokens", 0)
                    else:
                        agent_tokens += getattr(usage, "total_tokens", 0)
                
                result = AnalysisResult(
                    analysis_id=analysis_id,
                    node_name=node_name,
                    result_type=result_type,
                    title=title,
                    content=content,
                    tokens_used=agent_tokens
                )
                
                db.add(result)
        
        print(f"Saved {len(result_mappings)} analysis results")
    
    async def _mark_analysis_failed(
        self, 
        analysis_id: str, 
        error_message: str,
        db: AsyncSession
    ) -> None:
        """Mark analysis as failed in database."""
        
        try:
            update_stmt = (
                update(Analysis)
                .where(Analysis.id == UUID(analysis_id))
                .values(
                    status="failed",
                    error_message=error_message,
                    end_date=datetime.utcnow()
                )
            )
            
            await db.execute(update_stmt)
            await db.commit()
            
            print(f"❌ Marked analysis as failed: {analysis_id} - {error_message}")
            
        except Exception as e:
            print(f"Failed to update analysis status: {e}")
            await db.rollback()
    
    def _extract_recommendations(self, state: TrainingAnalysisState) -> Optional[str]:
        """Extract recommendations from synthesis and expert outputs."""
        
        # Primary source: synthesis analysis
        synthesis = state.get("synthesis_analysis")
        if synthesis:
            return synthesis
        
        # Fallback: extract from expert analyses
        recommendations = []
        for expert_key in ["metrics_expert_analysis", "physiology_expert_analysis", "activity_expert_analysis"]:
            expert_output = state.get(expert_key)
            if expert_output:
                recommendations.append(f"## {expert_key.title()}\n{expert_output}")
        
        return "\n\n".join(recommendations) if recommendations else None
    
    async def get_analysis_status(
        self, 
        analysis_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get current status of an analysis."""
        
        try:
            query = select(Analysis).where(Analysis.id == UUID(analysis_id))
            result = await db.execute(query)
            analysis = result.scalar_one_or_none()
            
            if not analysis:
                return {
                    "analysis_id": analysis_id,
                    "status": "not_found",
                    "error": "Analysis not found"
                }
            
            return {
                "analysis_id": str(analysis.id),
                "status": analysis.status,
                "progress_percentage": analysis.progress_percentage,
                "current_node": analysis.current_node,
                "total_tokens": analysis.total_tokens,
                "estimated_cost": analysis.estimated_cost,
                "error_message": analysis.error_message,
                "created_at": analysis.created_at,
                "updated_at": analysis.updated_at,
                "end_date": analysis.end_date
            }
            
        except Exception as e:
            return {
                "analysis_id": analysis_id,
                "status": "error",
                "error": f"Failed to get status: {str(e)}"
            }
    
    async def cancel_analysis(
        self, 
        analysis_id: str,
        db: AsyncSession
    ) -> bool:
        """Cancel a running analysis."""
        
        try:
            # Update analysis status to cancelled
            update_stmt = (
                update(Analysis)
                .where(Analysis.id == UUID(analysis_id))
                .values(
                    status="cancelled",
                    error_message="Analysis cancelled by user",
                    end_date=datetime.utcnow()
                )
            )
            
            await db.execute(update_stmt)
            await db.commit()
            
            print(f"🛑 Cancelled analysis: {analysis_id}")
            return True
            
        except Exception as e:
            print(f"Failed to cancel analysis: {e}")
            await db.rollback()
            return False


# Global analysis engine instance
analysis_engine = AnalysisEngine()