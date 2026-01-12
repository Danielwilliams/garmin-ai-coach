"""Training Analysis Workflow - LangGraph orchestration system.

This replicates the exact workflow structure from the CLI application
with the same parallel processing and conditional routing logic.
"""

from typing import Dict, Any, List
from datetime import datetime
from langgraph.graph import Graph, END, StateGraph
from langgraph.prebuilt import ToolExecutor

from app.services.ai.langgraph.state.training_analysis_state import (
    TrainingAnalysisState, 
    update_progress,
    add_error
)
from app.services.ai.status_tracker import ComponentStatus, ComponentType

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
        
        start_time = datetime.utcnow()
        tracker = state.get("status_tracker")
        
        try:
            if tracker:
                await tracker.log_data_extraction(
                    source="garmin_connect",
                    status=ComponentStatus.RUNNING,
                    message="Starting Garmin Connect data extraction"
                )
            
            state = update_progress(state, "data_extraction", 5.0)
            
            # Get training config from state
            training_config = state.get("training_config", {})
            
            if tracker:
                await tracker.log_event(
                    component_name="data_extraction",
                    component_type=ComponentType.DATA_EXTRACTION,
                    status=ComponentStatus.RUNNING,
                    message="Loading training configuration",
                    details={
                        "activities_days": training_config.get("activities_days", 21),
                        "metrics_days": training_config.get("metrics_days", 56),
                        "has_garmin_credentials": bool(training_config.get("garmin_email"))
                    }
                )
            
            # Create extraction configuration
            extraction_config = ExtractionConfig(
                activities_days=training_config.get("activities_days", 21),
                metrics_days=training_config.get("metrics_days", 56),
                include_detailed_activities=training_config.get("enable_plotting", False)
            )
            
            # Get Garmin credentials from training config or use mock data
            garmin_email = training_config.get("garmin_email")
            garmin_password = training_config.get("garmin_password_encrypted")
            
            # Check if we have real credentials
            has_real_credentials = garmin_email and garmin_password and garmin_email != "mock_user@example.com"
            
            if not has_real_credentials:
                garmin_email = "mock_user@example.com"
                garmin_password = "mock_password"
            
            use_real_data = has_real_credentials
            
            if tracker:
                await tracker.log_event(
                    component_name="credentials",
                    component_type=ComponentType.EXTERNAL_SERVICE,
                    status=ComponentStatus.WARNING if not has_real_credentials else ComponentStatus.RUNNING,
                    message=f"{'Processing real Garmin credentials' if use_real_data else 'No Garmin credentials found - using mock data. Please configure Garmin Connect in settings.'}",
                    details={
                        "data_source": "garmin_connect" if use_real_data else "mock_data",
                        "has_credentials": has_real_credentials,
                        "garmin_email": garmin_email if use_real_data else "none"
                    }
                )
            
            # Decrypt password if it's encrypted
            if garmin_password and garmin_password != "mock_password":
                try:
                    from app.core.security import decrypt_password
                    garmin_password = decrypt_password(garmin_password)
                    
                    if tracker:
                        await tracker.log_event(
                            component_name="credentials",
                            component_type=ComponentType.EXTERNAL_SERVICE,
                            status=ComponentStatus.SUCCESS,
                            message="Garmin credentials decrypted successfully"
                        )
                except Exception as e:
                    # Fall back to mock if decryption fails
                    garmin_password = "mock_password"
                    garmin_email = "mock_user@example.com"
                    
                    if tracker:
                        await tracker.log_event(
                            component_name="credentials",
                            component_type=ComponentType.EXTERNAL_SERVICE,
                            status=ComponentStatus.WARNING,
                            message="Failed to decrypt Garmin credentials, falling back to mock data",
                            error_details=str(e)
                        )
            
            if tracker:
                await tracker.log_data_extraction(
                    source="garmin_connect",
                    status=ComponentStatus.RUNNING,
                    message="Connecting to Garmin Connect API"
                )
            
            # Extract data using provided or mock credentials
            garmin_data = await extract_garmin_data(
                email=garmin_email,
                password=garmin_password,
                config=extraction_config
            )
            
            # Calculate extraction metrics
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            activities_count = len(garmin_data.activities) if garmin_data.activities else 0
            daily_stats_count = len(garmin_data.daily_stats) if garmin_data.daily_stats else 0
            
            if tracker:
                await tracker.log_data_extraction(
                    source="garmin_connect",
                    status=ComponentStatus.SUCCESS,
                    message=f"Data extraction completed successfully",
                    records_extracted=activities_count + daily_stats_count,
                    data_quality_score=garmin_data.data_completeness_score if hasattr(garmin_data, 'data_completeness_score') else 0.8,
                    duration_ms=duration_ms
                )
                
                await tracker.log_agent_progress(
                    agent_name="data_extraction",
                    status=ComponentStatus.SUCCESS,
                    message=f"Extracted {activities_count} activities and {daily_stats_count} daily stats",
                    progress_percentage=100.0,
                    duration_ms=duration_ms
                )
            
            # Store extracted data in state
            state["garmin_data"] = garmin_data.dict()
            state["user_profile"] = garmin_data.user_profile.dict() if garmin_data.user_profile else {}
            
            return state
            
        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            if tracker:
                await tracker.log_data_extraction(
                    source="garmin_connect",
                    status=ComponentStatus.ERROR,
                    message="Data extraction failed",
                    duration_ms=duration_ms,
                    error_details=str(e)
                )
                
                await tracker.log_agent_progress(
                    agent_name="data_extraction",
                    status=ComponentStatus.ERROR,
                    message="Data extraction failed",
                    progress_percentage=0.0,
                    duration_ms=duration_ms,
                    error_details=str(e)
                )
            
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