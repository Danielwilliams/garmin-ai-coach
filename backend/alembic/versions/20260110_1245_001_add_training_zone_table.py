"""Add training zone table

Revision ID: 001
Revises: 
Create Date: 2026-01-10 12:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add training zone table to store athlete training zones by discipline."""
    
    # Create training zone table
    op.create_table(
        'trainingzone',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True, 
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('training_config_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('discipline', sa.String(length=20), nullable=False),
        sa.Column('metric', sa.String(length=100), nullable=False),
        sa.Column('value', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create foreign key constraint to trainingconfig table
    op.create_foreign_key(
        'trainingzone_training_config_id_fkey',
        'trainingzone', 
        'trainingconfig',
        ['training_config_id'], 
        ['id'],
        ondelete='CASCADE'
    )
    
    # Create index on training_config_id for performance
    op.create_index('idx_trainingzone_config_id', 'trainingzone', ['training_config_id'])
    
    # Create index on discipline for filtering
    op.create_index('idx_trainingzone_discipline', 'trainingzone', ['discipline'])
    
    # Add check constraint for valid disciplines
    op.create_check_constraint(
        'ck_trainingzone_discipline',
        'trainingzone',
        "discipline IN ('Running', 'Cycling', 'Swimming')"
    )


def downgrade() -> None:
    """Remove training zone table."""
    
    # Drop indexes first
    op.drop_index('idx_trainingzone_discipline', table_name='trainingzone')
    op.drop_index('idx_trainingzone_config_id', table_name='trainingzone')
    
    # Drop check constraint
    op.drop_constraint('ck_trainingzone_discipline', 'trainingzone', type_='check')
    
    # Drop foreign key constraint
    op.drop_constraint('trainingzone_training_config_id_fkey', 'trainingzone', type_='foreignkey')
    
    # Drop the table
    op.drop_table('trainingzone')