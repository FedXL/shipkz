"""empty message

Revision ID: 4d249932a0b3
Revises: 25577d3ba58c
Create Date: 2023-11-07 13:12:17.696479

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d249932a0b3'
down_revision: Union[str, None] = '25577d3ba58c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
