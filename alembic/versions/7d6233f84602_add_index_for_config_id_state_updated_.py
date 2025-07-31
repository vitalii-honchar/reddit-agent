"""Add index for config_id, state, updated_at DESC

Revision ID: 7d6233f84602
Revises: 91ef27f17961
Create Date: 2025-07-31 09:37:22.111847

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d6233f84602'
down_revision: Union[str, Sequence[str], None] = '91ef27f17961'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create index for optimal query performance on config_id, state, updated_at DESC
    op.create_index(
        'ix_agent_execution_config_state_updated_at',
        'agent_execution',
        ['config_id', 'state', sa.text('updated_at DESC')],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the index
    op.drop_index('ix_agent_execution_config_state_updated_at', 'agent_execution')
