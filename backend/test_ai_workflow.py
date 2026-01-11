"""End-to-End AI Workflow Testing.

This script tests the complete AI analysis workflow with all 9 agents
to ensure proper integration and state management.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import workflow components
from app.services.ai.langgraph.state.training_analysis_state import TrainingAnalysisState, initialize_analysis_state
from app.services.ai.langgraph.workflows.training_analysis_workflow import workflow_engine


async def create_test_state() -> TrainingAnalysisState:
    """Create a test state for workflow testing."""
    
    analysis_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    training_config_id = str(uuid.uuid4())
    
    # Sample training configuration
    training_config = {
        "activities_days": 21,
        "metrics_days": 56,
        "analysis_context": "Base building phase",
        "ai_mode": "development",
        "enable_plotting": False,
        "hitl_enabled": False,
        "skip_synthesis": False
    }
    
    # Initialize the state
    initial_state = initialize_analysis_state(
        analysis_id=analysis_id,
        user_id=user_id,
        training_config_id=training_config_id,
        analysis_type="comprehensive",
        workflow_id="test_workflow",
        training_config=training_config
    )
    
    return initial_state


async def test_individual_agents():
    """Test individual AI agents separately."""
    
    logger.info("🧪 Testing individual AI agents...")
    
    # Create test state
    state = await create_test_state()
    
    # Mock some extracted data
    state["garmin_data"] = {
        "activities": [
            {
                "activity_id": "test_activity_1",
                "activity_type": "running",
                "duration_seconds": 3600,
                "distance_meters": 10000,
                "average_heart_rate": 155,
                "training_stress_score": 65,
                "perceived_exertion": 4,
                "start_time": datetime.utcnow()
            },
            {
                "activity_id": "test_activity_2", 
                "activity_type": "cycling",
                "duration_seconds": 5400,
                "distance_meters": 40000,
                "average_heart_rate": 145,
                "average_power": 250,
                "training_stress_score": 85,
                "perceived_exertion": 5,
                "start_time": datetime.utcnow()
            }
        ],
        "recovery_indicators": [
            {
                "measurement_date": datetime.utcnow().date(),
                "hrv_rmssd": 45.0,
                "training_readiness": 75,
                "sleep_score": 82,
                "stress_score": 25
            }
        ],
        "physiological_markers": [
            {
                "measurement_date": datetime.utcnow().date(),
                "vo2_max": 55.0,
                "training_stress_balance": 7.5,
                "acute_load": 450.0,
                "chronic_load": 420.0
            }
        ]
    }
    
    state["user_profile"] = {
        "display_name": "Test Athlete",
        "birth_date": "1985-06-15",
        "weight_kg": 70.0,
        "activity_level": "very_active"
    }
    
    try:
        # Test metrics summarizer
        logger.info("Testing metrics summarizer...")
        from app.services.ai.langgraph.nodes.metrics_summarizer_node import metrics_summarizer_node
        state = await metrics_summarizer_node(state)
        assert "metrics_summary" in state, "Metrics summary not generated"
        logger.info("✅ Metrics summarizer working")
        
        # Test physiology summarizer
        logger.info("Testing physiology summarizer...")
        from app.services.ai.langgraph.nodes.physiology_summarizer_node import physiology_summarizer_node
        state = await physiology_summarizer_node(state)
        assert "physiology_summary" in state, "Physiology summary not generated"
        logger.info("✅ Physiology summarizer working")
        
        # Test activity summarizer
        logger.info("Testing activity summarizer...")
        from app.services.ai.langgraph.nodes.activity_summarizer_node import activity_summarizer_node
        state = await activity_summarizer_node(state)
        assert "activity_summary" in state, "Activity summary not generated"
        logger.info("✅ Activity summarizer working")
        
        # Test expert agents
        logger.info("Testing expert agents...")
        from app.services.ai.langgraph.nodes.metrics_expert_node import metrics_expert_node
        from app.services.ai.langgraph.nodes.physiology_expert_node import physiology_expert_node
        from app.services.ai.langgraph.nodes.activity_expert_node import activity_expert_node
        
        state = await metrics_expert_node(state)
        assert "metrics_expert_analysis" in state, "Metrics expert analysis not generated"
        logger.info("✅ Metrics expert working")
        
        state = await physiology_expert_node(state)
        assert "physiology_expert_analysis" in state, "Physiology expert analysis not generated"
        logger.info("✅ Physiology expert working")
        
        state = await activity_expert_node(state)
        assert "activity_expert_analysis" in state, "Activity expert analysis not generated"
        logger.info("✅ Activity expert working")
        
        # Test synthesis
        logger.info("Testing synthesis agent...")
        from app.services.ai.langgraph.nodes.synthesis_node import synthesis_node
        state = await synthesis_node(state)
        assert "synthesis_analysis" in state, "Synthesis analysis not generated"
        logger.info("✅ Synthesis agent working")
        
        # Test formatting
        logger.info("Testing formatting agent...")
        from app.services.ai.langgraph.nodes.formatting_node import formatting_node
        state = await formatting_node(state)
        assert "formatted_report" in state, "Formatted report not generated"
        logger.info("✅ Formatting agent working")
        
        # Test planning
        logger.info("Testing planning agent...")
        from app.services.ai.langgraph.nodes.planning_node import planning_node
        state = await planning_node(state)
        assert "weekly_training_plan" in state, "Weekly training plan not generated"
        logger.info("✅ Planning agent working")
        
        logger.info("🎉 All individual agents working correctly!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Individual agent test failed: {e}")
        return False


async def test_complete_workflow():
    """Test the complete end-to-end workflow."""
    
    logger.info("🚀 Testing complete AI workflow...")
    
    try:
        # Create initial state
        initial_state = await create_test_state()
        
        logger.info(f"Starting workflow for analysis {initial_state['analysis_id']}")
        
        # Execute the complete workflow
        final_state = await workflow_engine.execute_workflow(initial_state)
        
        # Validate final state
        assert final_state["workflow_complete"] == True, "Workflow not marked as complete"
        assert "final_analysis_html" in final_state, "Final analysis HTML not generated"
        assert "final_planning_html" in final_state, "Final planning HTML not generated"
        assert "summary_json" in final_state, "Summary JSON not generated"
        
        # Check progress reached 100%
        progress = final_state.get("progress", {})
        assert progress.get("overall_percentage", 0) == 100.0, "Progress not at 100%"
        
        # Check token usage tracking
        token_usage = final_state.get("token_usage", {})
        assert len(token_usage) > 0, "No token usage tracked"
        
        # Check cost calculation
        total_cost = final_state.get("total_cost", 0)
        assert total_cost > 0, "No cost calculated"
        
        # Log results
        summary = final_state["summary_json"]
        logger.info(f"✅ Workflow completed successfully!")
        logger.info(f"   - Analysis ID: {summary['analysis_id']}")
        logger.info(f"   - Execution time: {summary['execution_time_minutes']:.2f} minutes")
        logger.info(f"   - Total cost: ${summary['total_cost']:.4f}")
        logger.info(f"   - Total tokens: {summary.get('total_tokens', 0):,}")
        logger.info(f"   - Agents completed: {len(summary.get('agents_completed', []))}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Complete workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_error_handling():
    """Test error handling and recovery."""
    
    logger.info("🛡️ Testing error handling...")
    
    try:
        # Create initial state with invalid configuration
        initial_state = await create_test_state()
        
        # Remove required data to trigger errors
        initial_state["training_config"] = {}  # Invalid config
        
        # Execute workflow - should handle errors gracefully
        final_state = await workflow_engine.execute_workflow(initial_state)
        
        # Check that errors were tracked
        errors = final_state.get("errors", [])
        logger.info(f"Captured {len(errors)} errors during execution")
        
        # Workflow should still complete even with errors
        assert final_state.get("workflow_complete", False), "Workflow should complete even with errors"
        
        logger.info("✅ Error handling working correctly!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error handling test failed: {e}")
        return False


async def test_state_management():
    """Test state management and data flow."""
    
    logger.info("📊 Testing state management...")
    
    try:
        initial_state = await create_test_state()
        
        # Test state updates
        from app.services.ai.langgraph.state.training_analysis_state import update_progress, add_token_usage, TokenUsage
        
        # Test progress updates
        updated_state = update_progress(initial_state, "test_step", 50.0)
        progress = updated_state.get("progress", {})
        assert progress.get("overall_percentage", 0) == 50.0, "Progress update failed"
        
        # Test token usage tracking
        token_usage = TokenUsage(
            total_tokens=1000,
            prompt_tokens=800,
            completion_tokens=200,
            model_used="claude-3-sonnet",
            provider="anthropic",
            estimated_cost=0.01
        )
        
        updated_state = add_token_usage(updated_state, "test_agent", token_usage)
        usage_data = updated_state.get("token_usage", {})
        assert "test_agent" in usage_data, "Token usage not tracked"
        
        logger.info("✅ State management working correctly!")
        return True
        
    except Exception as e:
        logger.error(f"❌ State management test failed: {e}")
        return False


async def main():
    """Run all tests."""
    
    logger.info("🧪 Starting comprehensive AI workflow testing...")
    
    tests = [
        ("State Management", test_state_management),
        ("Individual Agents", test_individual_agents),
        ("Error Handling", test_error_handling),
        ("Complete Workflow", test_complete_workflow),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n" + "="*60)
        logger.info(f"Running test: {test_name}")
        logger.info("="*60)
        
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Print summary
    logger.info(f"\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:<20} {status}")
        if not result:
            all_passed = False
    
    logger.info("="*60)
    final_status = "🎉 ALL TESTS PASSED!" if all_passed else "⚠️ SOME TESTS FAILED"
    logger.info(final_status)
    
    return all_passed


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())