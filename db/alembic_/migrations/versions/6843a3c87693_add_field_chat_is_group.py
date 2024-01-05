"""add field Chat.is_group

Revision ID: 6843a3c87693
Revises: da6acdddebe7
Create Date: 2023-12-16 15:06:03.648880

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6843a3c87693'
down_revision: Union[str, None] = 'da6acdddebe7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chats', sa.Column('is_group', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chats', 'is_group')
    # ### end Alembic commands ###