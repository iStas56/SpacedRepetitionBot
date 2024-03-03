"""Initial migration

Revision ID: d18987508697
Revises: 
Create Date: 2024-02-29 19:36:06.760417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd18987508697'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('user_words',
                  sa.Column('interval', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('user_words', 'interval')
