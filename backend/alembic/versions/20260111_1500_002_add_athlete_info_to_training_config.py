"""Add athlete information and Garmin credentials to training config

Revision ID: 002
Revises: 001
Create Date: 2026-01-11 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add athlete information and Garmin credentials to training config table."""
    
    # Add athlete information columns
    op.add_column('trainingconfig', sa.Column('athlete_name', sa.String(length=200), nullable=True))
    op.add_column('trainingconfig', sa.Column('athlete_email', sa.String(length=255), nullable=True))
    
    # Add training context columns
    op.add_column('trainingconfig', sa.Column('training_needs', sa.Text(), nullable=True))
    op.add_column('trainingconfig', sa.Column('session_constraints', sa.Text(), nullable=True))
    op.add_column('trainingconfig', sa.Column('training_preferences', sa.Text(), nullable=True))
    
    # Add Garmin Connect integration columns
    op.add_column('trainingconfig', sa.Column('garmin_email', sa.String(length=255), nullable=True))
    op.add_column('trainingconfig', sa.Column('garmin_password_encrypted', sa.Text(), nullable=True))
    op.add_column('trainingconfig', sa.Column('garmin_last_sync', sa.String(length=50), nullable=True))
    op.add_column('trainingconfig', sa.Column('garmin_is_connected', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    
    # Update existing records with default values
    op.execute("""
        UPDATE trainingconfig 
        SET 
            athlete_name = COALESCE(name, 'Unknown Athlete'),
            athlete_email = 'placeholder@example.com'
        WHERE athlete_name IS NULL OR athlete_email IS NULL
    """)
    
    # Now make the columns NOT NULL
    op.alter_column('trainingconfig', 'athlete_name', nullable=False)
    op.alter_column('trainingconfig', 'athlete_email', nullable=False)
    
    # Create indexes for performance
    op.create_index('idx_trainingconfig_athlete_email', 'trainingconfig', ['athlete_email'])
    op.create_index('idx_trainingconfig_garmin_email', 'trainingconfig', ['garmin_email'])


def downgrade() -> None:
    """Remove athlete information and Garmin credentials from training config."""
    
    # Drop indexes first
    op.drop_index('idx_trainingconfig_garmin_email', table_name='trainingconfig')
    op.drop_index('idx_trainingconfig_athlete_email', table_name='trainingconfig')
    
    # Drop all the added columns
    op.drop_column('trainingconfig', 'garmin_is_connected')
    op.drop_column('trainingconfig', 'garmin_last_sync')
    op.drop_column('trainingconfig', 'garmin_password_encrypted')
    op.drop_column('trainingconfig', 'garmin_email')
    op.drop_column('trainingconfig', 'training_preferences')
    op.drop_column('trainingconfig', 'session_constraints')
    op.drop_column('trainingconfig', 'training_needs')
    op.drop_column('trainingconfig', 'athlete_email')
    op.drop_column('trainingconfig', 'athlete_name')