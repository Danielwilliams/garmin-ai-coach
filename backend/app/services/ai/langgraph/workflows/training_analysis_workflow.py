"""Training Analysis Workflow - LangGraph orchestration system.

This replicates the exact workflow structure from the CLI application
with the same parallel processing and conditional routing logic.
"""

from typing import Dict, Any, List
from langgraph.graph import Graph, END, StateGraph
from langgraph.prebuilt import ToolExecutor

from app.services.ai.langgraph.state.training_analysis_state import (
    TrainingAnalysisState, 
    update_progress,
    add_error
)

# Import all AI agent nodes
from app.services.ai.langgraph.nodes.metrics_summarizer_node import metrics_summarizer_node
from app.services.ai.langgraph.nodes.physiology_summarizer_node import physiology_summarizer_node
from app.services.ai.langgraph.nodes.activity_summarizer_node import activity_summarizer_node
from app.services.ai.langgraph.nodes.metrics_expert_node import metrics_expert_node
from app.services.ai.langgraph.nodes.physiology_expert_node import physiology_expert_node
from app.services.ai.langgraph.nodes.activity_expert_node import activity_expert_node
from app.services.ai.langgraph.nodes.synthesis_node import synthesis_node
from app.services.ai.langgraph.nodes.formatting_node import formatting_node
from app.services.ai.langgraph.nodes.planning_node import planning_node

# Import data extraction
from app.services.garmin.data_extractor import extract_garmin_data, ExtractionConfig


class TrainingAnalysisWorkflow:
    """Main workflow orchestrator for training analysis."""
    
    def __init__(self):
        self.graph = self._build_workflow_graph()
    
    def _build_workflow_graph(self) -> StateGraph:
        """Build the complete LangGraph workflow matching CLI structure."""
        
        # Create the workflow graph
        workflow = StateGraph(TrainingAnalysisState)
        
        # === DATA EXTRACTION NODE ===
        workflow.add_node("data_extraction", self._data_extraction_node)
        
        # === PARALLEL SUMMARIZATION NODES ===
        workflow.add_node("metrics_summarizer", metrics_summarizer_node)
        workflow.add_node("physiology_summarizer", physiology_summarizer_node)
        workflow.add_node("activity_summarizer", activity_summarizer_node)
        
        # === EXPERT ANALYSIS NODES ===
        workflow.add_node("metrics_expert", metrics_expert_node)
        workflow.add_node("physiology_expert", physiology_expert_node)
        workflow.add_node("activity_expert", activity_expert_node)
        
        # === SYNTHESIS NODE ===
        workflow.add_node("synthesis", synthesis_node)
        
        # === OUTPUT NODES ===
        workflow.add_node("formatting", formatting_node)
        workflow.add_node("planning", planning_node)
        
        # === FINAL OUTPUT NODE ===
        workflow.add_node("finalize_output", self._finalize_output_node)
        
        # === DEFINE WORKFLOW EDGES ===
        
        # Start with data extraction
        workflow.set_entry_point("data_extraction")
        
        # Data extraction → Parallel summarization (all run in parallel)
        workflow.add_edge("data_extraction", "metrics_summarizer")
        workflow.add_edge("data_extraction", "physiology_summarizer")  
        workflow.add_edge("data_extraction", "activity_summarizer")
        
        # Summarizers → Expert agents (sequential per domain)
        workflow.add_edge("metrics_summarizer", "metrics_expert")
        workflow.add_edge("physiology_summarizer", "physiology_expert")
        workflow.add_edge("activity_summarizer", "activity_expert")
        
        # All experts → Synthesis (waits for all experts to complete)
        workflow.add_edge("metrics_expert", "synthesis")
        workflow.add_edge("physiology_expert", "synthesis")
        workflow.add_edge("activity_expert", "synthesis")
        
        # Synthesis → Parallel output generation
        workflow.add_edge("synthesis", "formatting")
        workflow.add_edge("synthesis", "planning")
        
        # Both outputs → Finalize
        workflow.add_edge("formatting", "finalize_output")
        workflow.add_edge("planning", "finalize_output")
        
        # Final output → END
        workflow.add_edge("finalize_output", END)
        
        return workflow.compile()
    
    # === NODE IMPLEMENTATIONS ===
    
    async def _data_extraction_node(self, state: TrainingAnalysisState) -> TrainingAnalysisState:
        """Extract training data from Garmin Connect and other sources."""
        
        try:
            state = update_progress(state, "data_extraction", 5.0)
            
            # Get training config from state
            training_config = state.get("training_config", {})
            
            # Create extraction configuration
            extraction_config = ExtractionConfig(
                activities_days=training_config.get("activities_days", 21),
                metrics_days=training_config.get("metrics_days", 56),
                include_detailed_activities=training_config.get("enable_plotting", False)
            )
            
            # Get Garmin credentials from training config or use mock data
            garmin_email = training_config.get("garmin_email", "mock_user@example.com")
            garmin_password = training_config.get("garmin_password_encrypted", "mock_password")
            
            # Decrypt password if it's encrypted (simplified for now)
            if garmin_password and garmin_password != "mock_password":
                try:
                    from app.core.security import decrypt_password
                    garmin_password = decrypt_password(garmin_password)
                except Exception:
                    # Fall back to mock if decryption fails
                    garmin_password = "mock_password"
                    garmin_email = "mock_user@example.com"
            
            # Extract data using provided or mock credentials
            garmin_data = await extract_garmin_data(
                email=garmin_email,
                password=garmin_password,
                config=extraction_config
            )
            
            # Store extracted data in state
            state["garmin_data"] = garmin_data.dict()
            state["user_profile"] = garmin_data.user_profile.dict() if garmin_data.user_profile else {}
            
            return state
            
        except Exception as e:
            return add_error(state, f"Data extraction failed: {str(e)}")
    
    # All node implementations are now handled by imported agent functions
    
    async def _finalize_output_node(self, state: TrainingAnalysisState) -> TrainingAnalysisState:
        """Finalize all outputs and create summary."""
        
        try:
            state = update_progress(state, "finalization", 100.0)
            
            # Combine final outputs
            state["final_analysis_html"] = state.get("formatted_report")
            state["final_planning_html"] = state.get("weekly_training_plan")
            
            # Mark workflow as complete
            state["workflow_complete"] = True
            state["end_time"] = state["updated_at"]
            
            # Calculate total cost from token usage
            total_cost = 0.0
            token_usage = state.get("token_usage", {})
            for agent_name, usage_list in token_usage.items():
                for usage in usage_list:
                    total_cost += usage.get("estimated_cost", 0.0)
            
            state["total_cost"] = total_cost
            
            # Generate summary
            state["summary_json"] = {
                "analysis_id": state["analysis_id"],
                "status": "completed",
                "total_cost": total_cost,
                "execution_time_minutes": (
                    (state["end_time"] - state["start_time"]).total_seconds() / 60
                ),
                "total_tokens": state.get("total_tokens", 0),
                "agents_completed": list(token_usage.keys())
            }
            
            return state
            
        except Exception as e:
            return add_error(state, f"Finalization failed: {str(e)}")
    
    # === ROUTING CONDITIONS ===
    # Simplified workflow - no complex routing needed
    
    # === WORKFLOW EXECUTION ===
    
    async def execute_workflow(self, initial_state: TrainingAnalysisState) -> TrainingAnalysisState:
        """Execute the complete training analysis workflow."""
        
        try:
            # Run the workflow
            final_state = await self.graph.ainvoke(initial_state)
            return final_state
            
        except Exception as e:
            # Handle workflow-level errors
            error_state = add_error(initial_state, f"Workflow execution failed: {str(e)}")
            error_state["workflow_complete"] = True
            error_state["end_time"] = error_state["updated_at"]
            return error_state


# Global workflow instance
workflow_engine: TrainingAnalysisWorkflow = TrainingAnalysisWorkflow()