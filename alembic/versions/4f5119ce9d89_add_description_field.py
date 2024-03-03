"""Add description field

Revision ID: 4f5119ce9d89
Revises: d18987508697
Create Date: 2024-03-01 06:16:43.887376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4f5119ce9d89'
down_revision: Union[str, None] = 'd18987508697'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('user_words', sa.Column('description', sa.String(), nullable=True))


def downgrade():
    op.drop_column('user_words', 'description')
