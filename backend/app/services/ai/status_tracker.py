"""Enhanced Status Tracking for AI Analysis System.

This module provides comprehensive status tracking for all components
of the AI analysis system including API connections, agent progress,
and detailed logging.
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
from uuid import uuid4

logger = logging.getLogger(__name__)


class ComponentStatus(Enum):
    """Status levels for different components."""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ComponentType(Enum):
    """Types of components being tracked."""
    API_CONNECTION = "api_connection"
    DATA_EXTRACTION = "data_extraction"
    AI_AGENT = "ai_agent"
    WORKFLOW_NODE = "workflow_node"
    DATABASE_OPERATION = "database_operation"
    EXTERNAL_SERVICE = "external_service"


@dataclass
class StatusEvent:
    """Individual status event with detailed information."""
    event_id: str
    timestamp: datetime
    component_type: ComponentType
    component_name: str
    status: ComponentStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    error_details: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


@dataclass
class ComponentHealth:
    """Health status of a component."""
    component_name: str
    component_type: ComponentType
    current_status: ComponentStatus
    last_updated: datetime
    total_events: int
    success_rate: float
    average_duration_ms: float
    last_error: Optional[str] = None
    recent_events: List[StatusEvent] = None


class AnalysisStatusTracker:
    """Comprehensive status tracker for analysis workflows."""
    
    def __init__(self, analysis_id: str):
        self.analysis_id = analysis_id
        self.events: List[StatusEvent] = []
        self.component_health: Dict[str, ComponentHealth] = {}
        self.start_time = datetime.utcnow()
        self.workflow_progress = {}
        self._lock = asyncio.Lock()
    
    async def log_event(
        self,
        component_name: str,
        component_type: ComponentType,
        status: ComponentStatus,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        error_details: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log a status event with comprehensive details."""
        
        async with self._lock:
            event = StatusEvent(
                event_id=str(uuid4()),
                timestamp=datetime.utcnow(),
                component_type=component_type,
                component_name=component_name,
                status=status,
                message=message,
                details=details,
                duration_ms=duration_ms,
                error_details=error_details,
                metrics=metrics
            )
            
            self.events.append(event)
            await self._update_component_health(event)
            
            # Log to standard logger with appropriate level
            log_message = f"[{self.analysis_id}] {component_name}: {message}"
            if details:
                log_message += f" | Details: {json.dumps(details, default=str)}"
            
            if status == ComponentStatus.ERROR:
                logger.error(log_message)
                if error_details:
                    logger.error(f"Error details: {error_details}")
            elif status == ComponentStatus.WARNING:
                logger.warning(log_message)
            elif status == ComponentStatus.SUCCESS:
                logger.info(log_message)
            else:
                logger.debug(log_message)
            
            return event.event_id
    
    async def _update_component_health(self, event: StatusEvent):
        """Update component health metrics based on new event."""
        
        component_name = event.component_name
        
        if component_name not in self.component_health:
            self.component_health[component_name] = ComponentHealth(
                component_name=component_name,
                component_type=event.component_type,
                current_status=event.status,
                last_updated=event.timestamp,
                total_events=0,
                success_rate=0.0,
                average_duration_ms=0.0,
                recent_events=[]
            )
        
        health = self.component_health[component_name]
        health.current_status = event.status
        health.last_updated = event.timestamp
        health.total_events += 1
        
        # Update recent events (keep last 10)
        if health.recent_events is None:
            health.recent_events = []
        health.recent_events.append(event)
        if len(health.recent_events) > 10:
            health.recent_events = health.recent_events[-10:]
        
        # Calculate success rate
        success_count = sum(1 for e in health.recent_events 
                          if e.status == ComponentStatus.SUCCESS)
        health.success_rate = success_count / len(health.recent_events) * 100
        
        # Calculate average duration
        durations = [e.duration_ms for e in health.recent_events 
                    if e.duration_ms is not None]
        if durations:
            health.average_duration_ms = sum(durations) / len(durations)
        
        # Store last error
        if event.status == ComponentStatus.ERROR:
            health.last_error = event.error_details or event.message
    
    async def log_api_connection(
        self,
        api_name: str,
        status: ComponentStatus,
        message: str,
        response_time_ms: Optional[int] = None,
        status_code: Optional[int] = None,
        error_details: Optional[str] = None
    ) -> str:
        """Log API connection status."""
        
        details = {}
        if status_code:
            details["status_code"] = status_code
        if response_time_ms:
            details["response_time_ms"] = response_time_ms
        
        return await self.log_event(
            component_name=f"api_{api_name}",
            component_type=ComponentType.API_CONNECTION,
            status=status,
            message=message,
            details=details,
            duration_ms=response_time_ms,
            error_details=error_details
        )
    
    async def log_agent_progress(
        self,
        agent_name: str,
        status: ComponentStatus,
        message: str,
        progress_percentage: Optional[float] = None,
        tokens_used: Optional[int] = None,
        model_used: Optional[str] = None,
        duration_ms: Optional[int] = None,
        error_details: Optional[str] = None
    ) -> str:
        """Log AI agent progress with detailed metrics."""
        
        details = {}
        metrics = {}
        
        if progress_percentage is not None:
            details["progress_percentage"] = progress_percentage
            self.workflow_progress[agent_name] = progress_percentage
        
        if tokens_used is not None:
            metrics["tokens_used"] = tokens_used
        
        if model_used:
            details["model_used"] = model_used
        
        return await self.log_event(
            component_name=f"agent_{agent_name}",
            component_type=ComponentType.AI_AGENT,
            status=status,
            message=message,
            details=details,
            duration_ms=duration_ms,
            error_details=error_details,
            metrics=metrics
        )
    
    async def log_data_extraction(
        self,
        source: str,
        status: ComponentStatus,
        message: str,
        records_extracted: Optional[int] = None,
        data_quality_score: Optional[float] = None,
        duration_ms: Optional[int] = None,
        error_details: Optional[str] = None
    ) -> str:
        """Log data extraction status."""
        
        details = {}
        metrics = {}
        
        if records_extracted is not None:
            metrics["records_extracted"] = records_extracted
        
        if data_quality_score is not None:
            details["data_quality_score"] = data_quality_score
        
        return await self.log_event(
            component_name=f"data_extract_{source}",
            component_type=ComponentType.DATA_EXTRACTION,
            status=status,
            message=message,
            details=details,
            duration_ms=duration_ms,
            error_details=error_details,
            metrics=metrics
        )
    
    async def log_workflow_node(
        self,
        node_name: str,
        status: ComponentStatus,
        message: str,
        input_size: Optional[int] = None,
        output_size: Optional[int] = None,
        duration_ms: Optional[int] = None,
        error_details: Optional[str] = None
    ) -> str:
        """Log workflow node execution."""
        
        details = {}
        
        if input_size is not None:
            details["input_size"] = input_size
        
        if output_size is not None:
            details["output_size"] = output_size
        
        return await self.log_event(
            component_name=f"node_{node_name}",
            component_type=ComponentType.WORKFLOW_NODE,
            status=status,
            message=message,
            details=details,
            duration_ms=duration_ms,
            error_details=error_details
        )
    
    def get_overall_progress(self) -> float:
        """Calculate overall analysis progress."""
        
        if not self.workflow_progress:
            return 0.0
        
        # Weight different agents based on importance
        agent_weights = {
            "data_extraction": 20.0,
            "activity_summarizer": 15.0,
            "metrics_expert": 20.0,
            "physiology_expert": 20.0,
            "activity_expert": 15.0,
            "synthesis": 25.0,
            "planning": 30.0
        }
        
        total_progress = 0.0
        total_weight = 0.0
        
        for agent, progress in self.workflow_progress.items():
            weight = agent_weights.get(agent, 10.0)
            total_progress += progress * weight
            total_weight += weight
        
        return total_progress / total_weight if total_weight > 0 else 0.0
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary."""
        
        now = datetime.utcnow()
        elapsed_time = (now - self.start_time).total_seconds()
        
        # Count events by status
        status_counts = {}
        for status in ComponentStatus:
            status_counts[status.value] = sum(
                1 for event in self.events if event.status == status
            )
        
        # Get recent errors
        recent_errors = [
            {
                "timestamp": event.timestamp.isoformat(),
                "component": event.component_name,
                "message": event.message,
                "error_details": event.error_details
            }
            for event in self.events[-10:]
            if event.status == ComponentStatus.ERROR
        ]
        
        return {
            "analysis_id": self.analysis_id,
            "overall_progress": self.get_overall_progress(),
            "elapsed_time_seconds": elapsed_time,
            "total_events": len(self.events),
            "status_counts": status_counts,
            "component_health": {
                name: {
                    "status": health.current_status.value,
                    "success_rate": health.success_rate,
                    "average_duration_ms": health.average_duration_ms,
                    "total_events": health.total_events,
                    "last_updated": health.last_updated.isoformat(),
                    "last_error": health.last_error
                }
                for name, health in self.component_health.items()
            },
            "workflow_progress": self.workflow_progress,
            "recent_errors": recent_errors
        }
    
    def get_detailed_timeline(self) -> List[Dict[str, Any]]:
        """Get detailed timeline of all events."""
        
        return [
            {
                "event_id": event.event_id,
                "timestamp": event.timestamp.isoformat(),
                "component_type": event.component_type.value,
                "component_name": event.component_name,
                "status": event.status.value,
                "message": event.message,
                "details": event.details,
                "duration_ms": event.duration_ms,
                "error_details": event.error_details,
                "metrics": event.metrics
            }
            for event in self.events
        ]


# Global tracker registry
_trackers: Dict[str, AnalysisStatusTracker] = {}


async def get_status_tracker(analysis_id: str) -> AnalysisStatusTracker:
    """Get or create status tracker for an analysis."""
    
    if analysis_id not in _trackers:
        _trackers[analysis_id] = AnalysisStatusTracker(analysis_id)
    
    return _trackers[analysis_id]


async def cleanup_tracker(analysis_id: str):
    """Clean up tracker when analysis is complete."""
    
    if analysis_id in _trackers:
        del _trackers[analysis_id]