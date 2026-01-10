"""Training profile API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
# from sqlalchemy.orm import selectinload  # Will add relationships later
from uuid import UUID

from app.database.base import get_db
from app.database.models.user import User, GarminAccount
from app.database.models.training_config import TrainingConfig, Competition, TrainingZone
from app.schemas.training_profile import (
    TrainingConfigCreate,
    TrainingConfigUpdate,
    TrainingConfigResponse,
    TrainingProfileSummary,
    TrainingProfileFormData,
    GarminCredentialsUpdate,
    GarminAccountResponse,
    CompetitionCreate,
    TrainingZoneCreate
)
from app.core.security import encrypt_password, decrypt_password
from app.dependencies import get_current_user

router = APIRouter(prefix="/training-profiles", tags=["training-profiles"])


@router.get("/", response_model=List[TrainingProfileSummary])
async def list_training_profiles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of user's training profiles with summary info."""
    
    # Query training configs with counts
    query = select(
        TrainingConfig,
        func.count(Competition.id).label('competitions_count'),
        func.count(TrainingZone.id).label('zones_count')
    ).outerjoin(
        Competition, Competition.training_config_id == TrainingConfig.id
    ).outerjoin(
        TrainingZone, TrainingZone.training_config_id == TrainingConfig.id
    ).where(
        TrainingConfig.user_id == current_user.id
    ).group_by(TrainingConfig.id).order_by(
        TrainingConfig.updated_at.desc()
    )
    
    result = await db.execute(query)
    profiles = result.all()
    
    return [
        TrainingProfileSummary(
            id=profile.TrainingConfig.id,
            name=profile.TrainingConfig.name,
            is_active=profile.TrainingConfig.is_active,
            competitions_count=profile.competitions_count,
            zones_count=profile.zones_count,
            ai_mode=profile.TrainingConfig.ai_mode,
            created_at=profile.TrainingConfig.created_at,
            updated_at=profile.TrainingConfig.updated_at
        )
        for profile in profiles
    ]


@router.get("/{profile_id}", response_model=TrainingConfigResponse)
async def get_training_profile(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific training profile with all related data."""
    
    # Get the training config
    query = select(TrainingConfig).where(
        and_(
            TrainingConfig.id == profile_id,
            TrainingConfig.user_id == current_user.id
        )
    )
    
    result = await db.execute(query)
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training profile not found"
        )
    
    # Get related training zones
    zones_query = select(TrainingZone).where(TrainingZone.training_config_id == profile_id)
    zones_result = await db.execute(zones_query)
    training_zones = zones_result.scalars().all()
    
    # Get related competitions
    competitions_query = select(Competition).where(Competition.training_config_id == profile_id)
    competitions_result = await db.execute(competitions_query)
    competitions = competitions_result.scalars().all()
    
    # Create response with related data
    profile_dict = {
        "id": profile.id,
        "user_id": profile.user_id,
        "name": profile.name,
        "is_active": profile.is_active,
        "analysis_context": profile.analysis_context,
        "planning_context": profile.planning_context,
        "activities_days": profile.activities_days,
        "metrics_days": profile.metrics_days,
        "ai_mode": profile.ai_mode,
        "enable_plotting": profile.enable_plotting,
        "hitl_enabled": profile.hitl_enabled,
        "skip_synthesis": profile.skip_synthesis,
        "output_directory": profile.output_directory,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
        "training_zones": [
            {
                "id": zone.id,
                "training_config_id": zone.training_config_id,
                "discipline": zone.discipline,
                "metric": zone.metric,
                "value": zone.value,
                "created_at": zone.created_at,
                "updated_at": zone.updated_at,
            }
            for zone in training_zones
        ],
        "competitions": [
            {
                "id": comp.id,
                "training_config_id": comp.training_config_id,
                "name": comp.name,
                "date": comp.date,
                "race_type": comp.race_type,
                "priority": comp.priority,
                "target_time": comp.target_time,
                "bikereg_id": comp.bikereg_id,
                "runreg_url": comp.runreg_url,
                "created_at": comp.created_at,
                "updated_at": comp.updated_at,
            }
            for comp in competitions
        ],
    }
    
    return TrainingConfigResponse.model_validate(profile_dict)


@router.post("/", response_model=TrainingConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_training_profile(
    profile_data: TrainingConfigCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new training profile."""
    
    # Check if name already exists for this user
    existing_query = select(TrainingConfig).where(
        and_(
            TrainingConfig.user_id == current_user.id,
            TrainingConfig.name == profile_data.name
        )
    )
    existing = await db.execute(existing_query)
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Training profile with this name already exists"
        )
    
    # Create training config
    training_config = TrainingConfig(
        user_id=current_user.id,
        name=profile_data.name,
        analysis_context=profile_data.analysis_context,
        planning_context=profile_data.planning_context,
        activities_days=profile_data.activities_days,
        metrics_days=profile_data.metrics_days,
        ai_mode=profile_data.ai_mode,
        enable_plotting=profile_data.enable_plotting,
        hitl_enabled=profile_data.hitl_enabled,
        skip_synthesis=profile_data.skip_synthesis,
        output_directory=profile_data.output_directory
    )
    
    db.add(training_config)
    await db.flush()  # Get the ID
    
    # Create training zones
    for zone_data in profile_data.training_zones:
        zone = TrainingZone(
            training_config_id=training_config.id,
            discipline=zone_data.discipline,
            metric=zone_data.metric,
            value=zone_data.value
        )
        db.add(zone)
    
    # Create competitions
    for comp_data in profile_data.competitions:
        competition = Competition(
            training_config_id=training_config.id,
            name=comp_data.name,
            date=comp_data.date,
            race_type=comp_data.race_type,
            priority=comp_data.priority,
            target_time=comp_data.target_time,
            bikereg_id=comp_data.bikereg_id,
            runreg_url=comp_data.runreg_url
        )
        db.add(competition)
    
    await db.commit()
    
    # Return the created profile with related data
    return await get_training_profile(training_config.id, current_user, db)


@router.post("/from-wizard", response_model=TrainingConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_training_profile_from_wizard(
    form_data: TrainingProfileFormData,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create training profile from frontend wizard form data."""
    
    # Update user's full name if provided
    if form_data.athlete_name != current_user.full_name:
        current_user.full_name = form_data.athlete_name
        db.add(current_user)
    
    # Generate profile name from athlete name and date
    from datetime import datetime
    profile_name = f"{form_data.athlete_name} - {datetime.now().strftime('%Y-%m-%d')}"
    
    # Check if name already exists, append number if needed
    counter = 1
    original_name = profile_name
    while True:
        existing_query = select(TrainingConfig).where(
            and_(
                TrainingConfig.user_id == current_user.id,
                TrainingConfig.name == profile_name
            )
        )
        existing = await db.execute(existing_query)
        if not existing.scalar_one_or_none():
            break
        counter += 1
        profile_name = f"{original_name} ({counter})"
    
    # Create training config
    training_config = TrainingConfig(
        user_id=current_user.id,
        name=profile_name,
        analysis_context=form_data.analysis_context,
        planning_context=form_data.planning_context,
        activities_days=form_data.activities_days,
        metrics_days=form_data.metrics_days,
        ai_mode=form_data.ai_mode,
        enable_plotting=form_data.enable_plotting,
        hitl_enabled=form_data.hitl_enabled,
        skip_synthesis=form_data.skip_synthesis,
        output_directory=form_data.output_directory
    )
    
    db.add(training_config)
    await db.flush()
    
    # Create training zones
    for zone_data in form_data.zones:
        zone = TrainingZone(
            training_config_id=training_config.id,
            discipline=zone_data.discipline,
            metric=zone_data.metric,
            value=zone_data.value
        )
        db.add(zone)
    
    # Create competitions (regular + external races)
    all_competitions = form_data.competitions + form_data.bikereg_events + form_data.runreg_events
    for comp_data in all_competitions:
        competition = Competition(
            training_config_id=training_config.id,
            name=comp_data.name,
            date=comp_data.date,
            race_type=comp_data.race_type,
            priority=comp_data.priority,
            target_time=comp_data.target_time,
            bikereg_id=comp_data.bikereg_id,
            runreg_url=comp_data.runreg_url
        )
        db.add(competition)
    
    # Handle Garmin credentials
    await _update_garmin_credentials(
        current_user.id,
        form_data.garmin_email,
        form_data.garmin_password,
        str(form_data.activities_days),
        str(form_data.metrics_days),
        db
    )
    
    await db.commit()
    
    # Return the created profile
    return await get_training_profile(training_config.id, current_user, db)


@router.put("/{profile_id}", response_model=TrainingConfigResponse)
async def update_training_profile(
    profile_id: UUID,
    profile_update: TrainingConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a training profile."""
    
    # Get existing profile
    query = select(TrainingConfig).where(
        and_(
            TrainingConfig.id == profile_id,
            TrainingConfig.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training profile not found"
        )
    
    # Update fields
    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    await db.commit()
    
    return await get_training_profile(profile_id, current_user, db)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_profile(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a training profile."""
    
    query = select(TrainingConfig).where(
        and_(
            TrainingConfig.id == profile_id,
            TrainingConfig.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training profile not found"
        )
    
    await db.delete(profile)
    await db.commit()


@router.put("/{profile_id}/activate", response_model=TrainingConfigResponse)
async def activate_training_profile(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Activate a training profile and deactivate others."""
    
    # Deactivate all user's profiles first
    from sqlalchemy import update
    await db.execute(
        update(TrainingConfig)
        .where(TrainingConfig.user_id == current_user.id)
        .values(is_active=False)
    )
    
    # Activate the specified profile
    query = select(TrainingConfig).where(
        and_(
            TrainingConfig.id == profile_id,
            TrainingConfig.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training profile not found"
        )
    
    profile.is_active = True
    await db.commit()
    
    return await get_training_profile(profile_id, current_user, db)


@router.put("/garmin-credentials", response_model=GarminAccountResponse)
async def update_garmin_credentials(
    credentials: GarminCredentialsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update Garmin Connect credentials."""
    
    await _update_garmin_credentials(
        current_user.id,
        credentials.email,
        credentials.password,
        "21",  # default values
        "56",
        db
    )
    
    await db.commit()
    
    # Return the updated Garmin account
    query = select(GarminAccount).where(GarminAccount.user_id == current_user.id)
    result = await db.execute(query)
    garmin_account = result.scalar_one_or_none()
    
    return GarminAccountResponse.model_validate(garmin_account)


async def _update_garmin_credentials(
    user_id: UUID,
    email: str,
    password: str,
    activities_days: str,
    metrics_days: str,
    db: AsyncSession
):
    """Helper function to update or create Garmin credentials."""
    
    # Get or create Garmin account
    query = select(GarminAccount).where(GarminAccount.user_id == user_id)
    result = await db.execute(query)
    garmin_account = result.scalar_one_or_none()
    
    encrypted_password = encrypt_password(password)
    
    if garmin_account:
        # Update existing
        garmin_account.email = email
        garmin_account.encrypted_password = encrypted_password
        garmin_account.activities_days = activities_days
        garmin_account.metrics_days = metrics_days
        garmin_account.is_connected = False  # Reset connection status
        garmin_account.sync_error = None
    else:
        # Create new
        garmin_account = GarminAccount(
            user_id=user_id,
            email=email,
            encrypted_password=encrypted_password,
            activities_days=activities_days,
            metrics_days=metrics_days,
            is_connected=False
        )
        db.add(garmin_account)