"""add cascade deleting for chat, user

Revision ID: da6acdddebe7
Revises: 75d5f22118fd
Create Date: 2023-12-06 04:47:27.930405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da6acdddebe7'
down_revision: Union[str, None] = '75d5f22118fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
