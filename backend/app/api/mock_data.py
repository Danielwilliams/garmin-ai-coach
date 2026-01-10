"""Mock data endpoints for testing analysis dashboard."""

from typing import List
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
import uuid

from app.database.models.user import User
from app.schemas.analysis import AnalysisSummary, AnalysisWithResults, AnalysisResultResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/mock", tags=["mock-data"])


@router.get("/analyses", response_model=List[AnalysisSummary])
async def get_mock_analyses(
    current_user: User = Depends(get_current_user)
):
    """Get mock analysis data for testing dashboard."""
    
    base_time = datetime.utcnow()
    
    mock_analyses = [
        AnalysisSummary(
            id=uuid.uuid4(),
            status="completed",
            analysis_type="full_analysis",
            progress_percentage=100,
            training_config_name="Spring Training 2024",
            total_tokens=15420,
            estimated_cost="$2.31",
            created_at=base_time - timedelta(days=2),
            has_summary=True,
            has_recommendations=True,
            has_weekly_plan=True,
            files_count=3,
            results_count=8
        ),
        AnalysisSummary(
            id=uuid.uuid4(),
            status="running",
            analysis_type="performance_analysis",
            progress_percentage=67,
            training_config_name="Marathon Prep 2024",
            total_tokens=8920,
            estimated_cost="$1.34",
            created_at=base_time - timedelta(hours=3),
            has_summary=True,
            has_recommendations=False,
            has_weekly_plan=False,
            files_count=1,
            results_count=4
        ),
        AnalysisSummary(
            id=uuid.uuid4(),
            status="completed",
            analysis_type="training_zones",
            progress_percentage=100,
            training_config_name="Base Building Phase",
            total_tokens=6840,
            estimated_cost="$1.03",
            created_at=base_time - timedelta(days=5),
            has_summary=True,
            has_recommendations=True,
            has_weekly_plan=True,
            files_count=2,
            results_count=5
        ),
        AnalysisSummary(
            id=uuid.uuid4(),
            status="failed",
            analysis_type="full_analysis",
            progress_percentage=23,
            training_config_name="Ironman Training",
            total_tokens=2450,
            estimated_cost="$0.37",
            created_at=base_time - timedelta(days=7),
            has_summary=False,
            has_recommendations=False,
            has_weekly_plan=False,
            files_count=0,
            results_count=1
        ),
        AnalysisSummary(
            id=uuid.uuid4(),
            status="pending",
            analysis_type="recovery_analysis",
            progress_percentage=0,
            training_config_name="Recovery Protocol",
            total_tokens=0,
            estimated_cost="$0.00",
            created_at=base_time - timedelta(minutes=15),
            has_summary=False,
            has_recommendations=False,
            has_weekly_plan=False,
            files_count=0,
            results_count=0
        )
    ]
    
    return mock_analyses


@router.get("/analyses/{analysis_id}", response_model=AnalysisWithResults)
async def get_mock_analysis_detail(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get mock detailed analysis data."""
    
    base_time = datetime.utcnow() - timedelta(days=2)
    
    mock_analysis = AnalysisWithResults(
        id=uuid.UUID(analysis_id) if analysis_id != "test" else uuid.uuid4(),
        user_id=current_user.id,
        training_config_id=uuid.uuid4(),
        status="completed",
        analysis_type="full_analysis",
        workflow_id="wf_spring_analysis_001",
        current_node="synthesis_node",
        progress_percentage=100,
        summary="""**Training Analysis Summary**

Your recent training data shows excellent progress in aerobic development with a 12% improvement in aerobic efficiency over the past 8 weeks. Key findings:

* **Aerobic Base**: Strong development with consistent Z2 work
* **Lactate Threshold**: Improved by 8 bpm, now at 171 bpm
* **VO2 Max**: Stable at 58 ml/kg/min with good repeatability
* **Training Load**: Well-managed with appropriate recovery periods

*Overall fitness trend is very positive for upcoming race goals.*""",
        recommendations="""**Training Recommendations**

Based on your analysis, here are the key recommendations:

1. **Continue Current Aerobic Base Work** - Your Z2 consistency is excellent
2. **Increase Threshold Work** - Add 1 weekly threshold session
3. **Speed Development** - Begin incorporating VO2 intervals
4. **Recovery Focus** - Maintain current recovery protocols

**Next 4 Weeks Priority:**
* Maintain 80/20 intensity distribution
* Focus on race-specific pacing
* Gradual build in weekly volume""",
        weekly_plan={
            "week_structure": {
                "monday": {"type": "recovery", "duration": "45-60min", "intensity": "Z1-Z2"},
                "tuesday": {"type": "threshold", "duration": "60-75min", "intensity": "Z3-Z4"},
                "wednesday": {"type": "aerobic", "duration": "90-120min", "intensity": "Z2"},
                "thursday": {"type": "intervals", "duration": "45-60min", "intensity": "Z4-Z5"},
                "friday": {"type": "recovery", "duration": "30-45min", "intensity": "Z1"},
                "saturday": {"type": "long", "duration": "150-180min", "intensity": "Z2-Z3"},
                "sunday": {"type": "rest", "duration": "0min", "intensity": "rest"}
            },
            "weekly_volume": "7.5-9 hours",
            "intensity_distribution": {"z1_z2": "80%", "z3_z4": "15%", "z5": "5%"}
        },
        start_date=base_time,
        end_date=base_time + timedelta(minutes=45),
        data_summary={
            "activities_analyzed": 28,
            "total_training_time": "32.5 hours",
            "avg_weekly_volume": "8.1 hours",
            "disciplines": {"running": "18.2h", "cycling": "12.1h", "swimming": "2.2h"}
        },
        total_tokens=15420,
        estimated_cost="$2.31",
        error_message=None,
        retry_count=0,
        created_at=base_time,
        updated_at=base_time + timedelta(minutes=45),
        training_config_name="Spring Training 2024",
        results=[
            AnalysisResultResponse(
                id=uuid.uuid4(),
                analysis_id=uuid.UUID(analysis_id) if analysis_id != "test" else uuid.uuid4(),
                node_name="physiology_expert",
                result_type="summary",
                title="Physiological Analysis",
                content="""**Aerobic System Analysis**

Your aerobic system shows strong adaptation with:
- Improved aerobic efficiency (12% increase)
- Enhanced fat oxidation capacity
- Better cardiac output at submaximal intensities

**Lactate Dynamics**:
- LT1: ~145 bpm (improved from 140 bpm)
- LT2: ~171 bpm (improved from 163 bpm)
- Good lactate clearance capacity""",
                data={"lt1_bpm": 145, "lt2_bpm": 171, "vo2_max": 58.2, "efficiency_improvement": 12},
                file_path=None,
                tokens_used=2340,
                processing_time=45,
                created_at=base_time + timedelta(minutes=10),
                updated_at=base_time + timedelta(minutes=10)
            ),
            AnalysisResultResponse(
                id=uuid.uuid4(),
                analysis_id=uuid.UUID(analysis_id) if analysis_id != "test" else uuid.uuid4(),
                node_name="activity_expert", 
                result_type="recommendation",
                title="Training Load Recommendations",
                content="""**Current Training Load Assessment**

Your training load management is excellent with:
- Appropriate CTL progression (TSS ramp rate: 5-8/week)
- Good TSB management for key sessions
- Effective recovery integration

**Recommendations**:
- Continue current load progression
- Add one weekly threshold session
- Maintain recovery week every 4th week""",
                data={"ctl": 78, "atl": 68, "tsb": 10, "weekly_tss": 520},
                file_path=None,
                tokens_used=1890,
                processing_time=32,
                created_at=base_time + timedelta(minutes=15),
                updated_at=base_time + timedelta(minutes=15)
            ),
            AnalysisResultResponse(
                id=uuid.uuid4(),
                analysis_id=uuid.UUID(analysis_id) if analysis_id != "test" else uuid.uuid4(),
                node_name="season_planner",
                result_type="plan",
                title="4-Week Training Block",
                content="""**Weeks 1-4 Training Focus**

*Week 1: Build Introduction*
- Add 1 threshold session
- Maintain aerobic volume
- Recovery focus on sleep

*Week 2: Adaptation*
- Continue threshold work
- Introduce tempo efforts
- Monitor recovery metrics

*Week 3: Integration*
- Race-specific intervals
- Practice nutrition
- Taper volume slightly

*Week 4: Recovery*
- 70% of normal volume
- Easy aerobic focus
- Preparation for next block""",
                data={"block_type": "build", "duration_weeks": 4, "volume_progression": [100, 105, 110, 70]},
                file_path="/storage/plans/4week_block_plan.html",
                tokens_used=2120,
                processing_time=38,
                created_at=base_time + timedelta(minutes=25),
                updated_at=base_time + timedelta(minutes=25)
            )
        ],
        files=[
            {
                "id": uuid.uuid4(),
                "analysis_id": uuid.UUID(analysis_id) if analysis_id != "test" else uuid.uuid4(),
                "filename": "training_analysis_report.html",
                "file_type": "report",
                "mime_type": "text/html",
                "file_size": 245680,
                "file_path": "/storage/reports/training_analysis_report.html",
                "is_public": False,
                "download_count": 3,
                "created_at": base_time + timedelta(minutes=40),
                "updated_at": base_time + timedelta(minutes=40)
            },
            {
                "id": uuid.uuid4(),
                "analysis_id": uuid.UUID(analysis_id) if analysis_id != "test" else uuid.uuid4(),
                "filename": "power_curve_analysis.png",
                "file_type": "plot",
                "mime_type": "image/png",
                "file_size": 87340,
                "file_path": "/storage/plots/power_curve_analysis.png",
                "is_public": False,
                "download_count": 1,
                "created_at": base_time + timedelta(minutes=42),
                "updated_at": base_time + timedelta(minutes=42)
            }
        ]
    )
    
    return mock_analysis