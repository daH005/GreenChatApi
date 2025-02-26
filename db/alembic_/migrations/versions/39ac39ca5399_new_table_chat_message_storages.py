"""new table chat_message_storages

Revision ID: 39ac39ca5399
Revises: d763b7396933
Create Date: 2025-01-11 01:19:17.841067

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '39ac39ca5399'
down_revision: Union[str, None] = 'd763b7396933'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat_message_storages',
    sa.Column('chat_message_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['chat_message_id'], ['chat_messages.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('chat_messages', 'storage_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat_messages', sa.Column('storage_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.drop_table('chat_message_storages')
    # ### end Alembic commands ###
