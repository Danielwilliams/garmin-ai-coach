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
    create_initial_state, 
    TrainingAnalysisState
)
from app.services.ai.langgraph.workflows.training_analysis_workflow import workflow_engine
from app.database.models.analysis import Analysis
from app.database.models.training_config import TrainingConfig
from sqlalchemy.ext.asyncio import AsyncSession


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
        
        # Create initial analysis state
        initial_state = create_initial_state(
            analysis_id=analysis_id,
            user_id=user_id,
            training_config_id=training_config_id,
            analysis_config=analysis_config
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
        
        # TODO: Implement actual database loading
        # This is a placeholder that will be replaced with real DB loading
        
        return {
            "id": training_config_id,
            "name": "Sample Training Config",
            "analysis_context": "Sample analysis context",
            "planning_context": "Sample planning context",
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
        
        # TODO: Create actual Analysis model instance
        # This will integrate with the existing database models
        
        analysis_data = {
            "id": state["analysis_id"],
            "user_id": state["user_id"],
            "training_config_id": state["training_config_id"],
            "status": "pending",
            "analysis_type": state["analysis_type"],
            "workflow_id": state["workflow_id"],
            "progress_percentage": 0,
            "created_at": state["created_at"]
        }
        
        print(f"📊 Created analysis record: {analysis_data}")
    
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
        
        # TODO: Implement actual database saving
        # This will save all the results, files, and metadata
        
        results_data = {
            "analysis_id": final_state["analysis_id"],
            "status": "completed" if final_state["workflow_complete"] else "failed",
            "progress_percentage": final_state["progress"].progress_percentage,
            "summary": final_state.get("synthesis_output"),
            "recommendations": self._extract_recommendations(final_state),
            "weekly_plan": final_state.get("weekly_plan"),
            "total_tokens": sum(
                usage.total_tokens for usage in final_state["token_usage"].values()
            ),
            "estimated_cost": final_state["total_cost"],
            "final_analysis_html": final_state.get("final_analysis_html"),
            "final_planning_html": final_state.get("final_planning_html"),
            "end_date": final_state.get("end_time"),
            "summary_json": final_state.get("summary_json")
        }
        
        print(f"💾 Saving analysis results: {results_data}")
    
    async def _mark_analysis_failed(
        self, 
        analysis_id: str, 
        error_message: str,
        db: AsyncSession
    ) -> None:
        """Mark analysis as failed in database."""
        
        # TODO: Update analysis status in database
        
        print(f"❌ Marking analysis as failed: {analysis_id} - {error_message}")
    
    def _extract_recommendations(self, state: TrainingAnalysisState) -> Optional[str]:
        """Extract recommendations from expert outputs."""
        
        recommendations = []
        
        # Gather recommendations from all expert outputs
        for expert_key in ["metrics_expert_output", "physiology_expert_output", "activity_expert_output"]:
            expert_output = state.get(expert_key)
            if expert_output and expert_output.recommendations:
                recommendations.extend(expert_output.recommendations)
        
        return "\n".join(recommendations) if recommendations else None
    
    async def get_analysis_status(
        self, 
        analysis_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get current status of an analysis."""
        
        # TODO: Load from database
        # For now return placeholder status
        
        return {
            "analysis_id": analysis_id,
            "status": "running",
            "progress_percentage": 45.0,
            "current_step": "expert_analysis",
            "estimated_completion": None,
            "errors": [],
            "created_at": datetime.utcnow()
        }
    
    async def cancel_analysis(
        self, 
        analysis_id: str,
        db: AsyncSession
    ) -> bool:
        """Cancel a running analysis."""
        
        # TODO: Implement analysis cancellation
        # This would involve stopping the workflow and updating status
        
        print(f"🛑 Cancelling analysis: {analysis_id}")
        return True


# Global analysis engine instance
analysis_engine = AnalysisEngine()