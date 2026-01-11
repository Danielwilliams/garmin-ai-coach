"""Analysis Database Service.

This service handles all database operations for training analyses,
providing a clean interface for the AI analysis engine.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID, uuid4
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload

from app.database.models.analysis import Analysis, AnalysisResult, AnalysisFile
from app.database.models.training_config import TrainingConfig
from app.services.ai.langgraph.state.training_analysis_state import TrainingAnalysisState

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for managing analysis data in the database."""
    
    async def create_analysis(
        self,
        state: TrainingAnalysisState,
        db: AsyncSession
    ) -> Analysis:
        """Create a new analysis record."""
        
        try:
            analysis = Analysis(
                id=UUID(state["analysis_id"]),
                user_id=UUID(state["user_id"]),
                training_config_id=UUID(state["training_config_id"]),
                status="running",
                analysis_type=state["analysis_type"],
                workflow_id=state["workflow_id"],
                progress_percentage=0.0,
                total_tokens=0,
                estimated_cost="$0.00",
                retry_count=0
            )
            
            db.add(analysis)
            await db.commit()
            await db.refresh(analysis)
            
            logger.info(f"📊 Created analysis record: {analysis.id}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to create analysis: {e}")
            await db.rollback()
            raise
    
    async def update_analysis_progress(
        self,
        analysis_id: str,
        current_node: str,
        progress_percentage: float,
        db: AsyncSession
    ) -> None:
        """Update analysis progress."""
        
        try:
            stmt = (
                update(Analysis)
                .where(Analysis.id == UUID(analysis_id))
                .values(
                    current_node=current_node,
                    progress_percentage=progress_percentage,
                    updated_at=datetime.utcnow()
                )
            )
            
            await db.execute(stmt)
            await db.commit()
            
            logger.debug(f"Updated analysis {analysis_id} progress: {progress_percentage}%")
            
        except Exception as e:
            logger.error(f"❌ Failed to update progress: {e}")
            await db.rollback()
            raise
    
    async def save_analysis_results(
        self,
        final_state: TrainingAnalysisState,
        db: AsyncSession
    ) -> None:
        """Save complete analysis results to database."""
        
        try:
            analysis_id = UUID(final_state["analysis_id"])
            
            # Calculate totals
            total_tokens = final_state.get("total_tokens", 0)
            total_cost = final_state.get("total_cost", 0.0)
            
            # Update main analysis record
            progress = final_state.get("progress", {})
            
            update_stmt = (
                update(Analysis)
                .where(Analysis.id == analysis_id)
                .values(
                    status="completed" if final_state.get("workflow_complete") else "failed",
                    progress_percentage=progress.get("progress_percentage", 100.0),
                    summary=final_state.get("synthesis_analysis"),
                    recommendations=self._extract_recommendations(final_state),
                    weekly_plan=self._extract_weekly_plan(final_state),
                    total_tokens=total_tokens,
                    estimated_cost=f"${total_cost:.4f}",
                    end_date=final_state.get("end_time"),
                    error_message=None if final_state.get("workflow_complete") else "Workflow failed",
                    data_summary=self._extract_data_summary(final_state)
                )
            )
            
            await db.execute(update_stmt)
            
            # Save individual results
            await self._save_individual_results(final_state, db)
            
            # Save generated files
            await self._save_generated_files(final_state, db)
            
            await db.commit()
            
            logger.info(f"💾 Saved complete analysis results for {analysis_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save analysis results: {e}")
            await db.rollback()
            raise
    
    async def _save_individual_results(
        self,
        final_state: TrainingAnalysisState,
        db: AsyncSession
    ) -> None:
        """Save individual agent results as AnalysisResult records."""
        
        analysis_id = UUID(final_state["analysis_id"])
        
        # Define result mappings
        result_mappings = [
            ("metrics_summary", "metrics_summarizer", "summary", "Training Metrics Summary"),
            ("physiology_summary", "physiology_summarizer", "summary", "Physiology & Recovery Summary"),
            ("activity_summary", "activity_summarizer", "summary", "Activity Pattern Summary"),
            ("metrics_expert_analysis", "metrics_expert", "expert_analysis", "Advanced Metrics Analysis"),
            ("physiology_expert_analysis", "physiology_expert", "expert_analysis", "Advanced Physiology Analysis"),
            ("activity_expert_analysis", "activity_expert", "expert_analysis", "Advanced Activity Analysis"),
            ("synthesis_analysis", "synthesis", "comprehensive", "Integrated Analysis"),
            ("formatted_report", "formatting", "report", "Formatted Analysis Report"),
            ("weekly_training_plan", "planning", "plan", "Weekly Training Plan")
        ]
        
        # Save each result
        for state_key, node_name, result_type, title in result_mappings:
            content = final_state.get(state_key)
            if content:
                # Get processing stats
                tokens_used = self._get_tokens_for_agent(final_state, node_name)
                processing_time = self._get_processing_time(final_state, node_name)
                
                result = AnalysisResult(
                    analysis_id=analysis_id,
                    node_name=node_name,
                    result_type=result_type,
                    title=title,
                    content=content,
                    tokens_used=tokens_used,
                    processing_time=processing_time
                )
                
                db.add(result)
        
        logger.info(f\"Saved {len([m for m in result_mappings if final_state.get(m[0])])} analysis results\")
    
    async def _save_generated_files(
        self,
        final_state: TrainingAnalysisState,
        db: AsyncSession
    ) -> None:
        \"\"\"Save generated file records.\"\"\"
        
        analysis_id = UUID(final_state[\"analysis_id\"])
        output_files = final_state.get(\"output_files\", [])
        
        for file_path in output_files:
            if file_path and isinstance(file_path, str):
                # Extract file info
                filename = file_path.split(\"/\")[-1]
                file_type = self._determine_file_type(filename)
                mime_type = self._determine_mime_type(filename)
                
                analysis_file = AnalysisFile(
                    analysis_id=analysis_id,
                    filename=filename,
                    file_type=file_type,
                    mime_type=mime_type,
                    file_size=0,  # Would be calculated in real implementation
                    file_path=file_path,
                    is_public=False,
                    download_count=0
                )
                
                db.add(analysis_file)
        
        if output_files:
            logger.info(f\"Saved {len(output_files)} file references\")
    
    async def get_analysis(
        self,
        analysis_id: str,
        user_id: str,
        db: AsyncSession
    ) -> Optional[Analysis]:
        \"\"\"Get analysis with all related data.\"\"\"
        
        try:
            query = (
                select(Analysis)
                .options(
                    selectinload(Analysis.results),
                    selectinload(Analysis.files)
                )
                .where(
                    and_(
                        Analysis.id == UUID(analysis_id),
                        Analysis.user_id == UUID(user_id)
                    )
                )
            )
            
            result = await db.execute(query)
            analysis = result.scalar_one_or_none()
            
            return analysis
            
        except Exception as e:
            logger.error(f\"❌ Failed to get analysis: {e}\")
            return None
    
    async def list_user_analyses(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
        db: AsyncSession
    ) -> List[Analysis]:
        \"\"\"List user's analyses with pagination.\"\"\"
        
        try:
            query = select(Analysis).where(Analysis.user_id == UUID(user_id))
            
            if status:
                query = query.where(Analysis.status == status)
            
            query = (
                query
                .order_by(Analysis.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            
            result = await db.execute(query)
            analyses = result.scalars().all()
            
            return list(analyses)
            
        except Exception as e:
            logger.error(f\"❌ Failed to list analyses: {e}\")
            return []
    
    async def mark_analysis_failed(
        self,
        analysis_id: str,
        error_message: str,
        db: AsyncSession
    ) -> None:
        \"\"\"Mark analysis as failed.\"\"\"
        
        try:
            stmt = (
                update(Analysis)
                .where(Analysis.id == UUID(analysis_id))
                .values(
                    status=\"failed\",
                    error_message=error_message,
                    end_date=datetime.utcnow(),
                    progress_percentage=0.0
                )
            )
            
            await db.execute(stmt)
            await db.commit()
            
            logger.info(f\"❌ Marked analysis {analysis_id} as failed: {error_message}\")
            
        except Exception as e:
            logger.error(f\"❌ Failed to mark analysis as failed: {e}\")
            await db.rollback()
            raise
    
    async def cancel_analysis(
        self,
        analysis_id: str,
        user_id: str,
        db: AsyncSession
    ) -> bool:
        \"\"\"Cancel a running analysis.\"\"\"
        
        try:
            stmt = (
                update(Analysis)
                .where(
                    and_(
                        Analysis.id == UUID(analysis_id),
                        Analysis.user_id == UUID(user_id),
                        Analysis.status.in_([\"pending\", \"running\"])
                    )
                )
                .values(
                    status=\"cancelled\",
                    error_message=\"Analysis cancelled by user\",
                    end_date=datetime.utcnow()
                )
            )
            
            result = await db.execute(stmt)
            await db.commit()
            
            cancelled = result.rowcount > 0
            
            if cancelled:
                logger.info(f\"🛑 Cancelled analysis {analysis_id}\")
            
            return cancelled
            
        except Exception as e:
            logger.error(f\"❌ Failed to cancel analysis: {e}\")
            await db.rollback()
            return False
    
    async def get_analysis_status(
        self,
        analysis_id: str,
        user_id: str,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        \"\"\"Get current analysis status.\"\"\"
        
        try:
            query = (
                select(Analysis)
                .where(
                    and_(
                        Analysis.id == UUID(analysis_id),
                        Analysis.user_id == UUID(user_id)
                    )
                )
            )
            
            result = await db.execute(query)
            analysis = result.scalar_one_or_none()
            
            if not analysis:
                return None
            
            return {
                \"analysis_id\": str(analysis.id),
                \"status\": analysis.status,
                \"progress_percentage\": analysis.progress_percentage,
                \"current_node\": analysis.current_node,
                \"total_tokens\": analysis.total_tokens,
                \"estimated_cost\": analysis.estimated_cost,
                \"error_message\": analysis.error_message,
                \"created_at\": analysis.created_at,
                \"updated_at\": analysis.updated_at,
                \"end_date\": analysis.end_date
            }
            
        except Exception as e:
            logger.error(f\"❌ Failed to get analysis status: {e}\")
            return None
    
    async def get_user_analysis_stats(
        self,
        user_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        \"\"\"Get user's analysis statistics.\"\"\"
        
        try:
            # This would normally use aggregate functions
            # For now, we'll get all analyses and calculate stats
            all_analyses = await self.list_user_analyses(user_id, limit=1000, db=db)
            
            total_analyses = len(all_analyses)
            completed = len([a for a in all_analyses if a.status == \"completed\"])
            running = len([a for a in all_analyses if a.status == \"running\"])
            failed = len([a for a in all_analyses if a.status == \"failed\"])
            
            total_tokens = sum(a.total_tokens for a in all_analyses)
            
            # Calculate total cost
            total_cost = 0.0
            for analysis in all_analyses:
                if analysis.estimated_cost:
                    try:
                        cost_str = analysis.estimated_cost.replace(\"$\", \"\")
                        total_cost += float(cost_str)
                    except ValueError:
                        continue
            
            return {
                \"total_analyses\": total_analyses,
                \"completed_analyses\": completed,
                \"running_analyses\": running,
                \"failed_analyses\": failed,
                \"total_tokens_used\": total_tokens,
                \"total_cost_usd\": total_cost
            }
            
        except Exception as e:
            logger.error(f\"❌ Failed to get analysis stats: {e}\")
            return {
                \"total_analyses\": 0,
                \"completed_analyses\": 0,
                \"running_analyses\": 0,
                \"failed_analyses\": 0,
                \"total_tokens_used\": 0,
                \"total_cost_usd\": 0.0
            }
    
    # Helper methods
    
    def _extract_recommendations(self, state: TrainingAnalysisState) -> Optional[str]:
        \"\"\"Extract recommendations from state.\"\"\"
        
        # Try synthesis first
        synthesis = state.get(\"synthesis_analysis\")
        if synthesis:
            return synthesis
        
        # Fallback to expert analyses
        recommendations = []
        for key in [\"metrics_expert_analysis\", \"physiology_expert_analysis\", \"activity_expert_analysis\"]:
            analysis = state.get(key)
            if analysis:
                recommendations.append(f\"### {key.replace('_', ' ').title()}\
{analysis}\")
        
        return \"\
\
\".join(recommendations) if recommendations else None
    
    def _extract_weekly_plan(self, state: TrainingAnalysisState) -> Optional[Dict[str, Any]]:
        \"\"\"Extract weekly plan as structured data.\"\"\"
        
        plan_text = state.get(\"weekly_training_plan\")
        if not plan_text:
            return None
        
        # For now, store as text in a structured format
        # In a real implementation, this might parse the plan into structured days/sessions
        return {
            \"plan_text\": plan_text,
            \"generated_at\": datetime.utcnow().isoformat(),
            \"format\": \"text\"
        }
    
    def _extract_data_summary(self, state: TrainingAnalysisState) -> Optional[Dict[str, Any]]:
        \"\"\"Extract data summary for storage.\"\"\"
        
        garmin_data = state.get(\"garmin_data\", {})
        if not garmin_data:
            return None
        
        return {
            \"total_activities\": len(garmin_data.get(\"activities\", [])),
            \"analysis_period_days\": state.get(\"activities_days\", 21),
            \"metrics_period_days\": state.get(\"metrics_days\", 56),
            \"data_sources\": [\"garmin_connect\"],  # Could be extended
            \"extraction_date\": state.get(\"created_at\", datetime.utcnow()).isoformat()
        }
    
    def _get_tokens_for_agent(self, state: TrainingAnalysisState, agent_name: str) -> int:
        \"\"\"Get token usage for specific agent.\"\"\"
        
        token_usage = state.get(\"token_usage\", {})
        agent_usage = token_usage.get(agent_name, [])
        
        total_tokens = 0
        for usage in agent_usage:
            if isinstance(usage, dict):
                total_tokens += usage.get(\"total_tokens\", 0)
            else:
                total_tokens += getattr(usage, \"total_tokens\", 0)
        
        return total_tokens
    
    def _get_processing_time(self, state: TrainingAnalysisState, agent_name: str) -> Optional[int]:
        \"\"\"Get processing time for specific agent.\"\"\"
        
        # This would be tracked during execution
        # For now, return None (could be calculated from timestamps)
        return None
    
    def _determine_file_type(self, filename: str) -> str:
        \"\"\"Determine file type from filename.\"\"\"
        
        extension = filename.split(\".\")[-1].lower() if \".\" in filename else \"\"
        
        if extension in [\"png\", \"jpg\", \"jpeg\", \"svg\"]:
            return \"plot\"
        elif extension in [\"html\", \"htm\"]:
            return \"report\"
        elif extension in [\"json\", \"csv\"]:
            return \"data\"
        else:
            return \"other\"
    
    def _determine_mime_type(self, filename: str) -> str:
        \"\"\"Determine MIME type from filename.\"\"\"
        
        extension = filename.split(\".\")[-1].lower() if \".\" in filename else \"\"
        
        mime_types = {
            \"png\": \"image/png\",
            \"jpg\": \"image/jpeg\",
            \"jpeg\": \"image/jpeg\",
            \"svg\": \"image/svg+xml\",
            \"html\": \"text/html\",
            \"htm\": \"text/html\",
            \"json\": \"application/json\",
            \"csv\": \"text/csv\",
            \"pdf\": \"application/pdf\"
        }
        
        return mime_types.get(extension, \"application/octet-stream\")


# Global service instance
analysis_service = AnalysisService()