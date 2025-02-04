"""tokens

Revision ID: 951214715243
Revises: d21ef21c2962
Create Date: 2025-02-04 18:45:30.148069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '951214715243'
down_revision: Union[str, None] = 'd21ef21c2962'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auth_tokens',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=500), nullable=False),
    sa.Column('is_refresh', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('value')
    )
    op.drop_index('jti', table_name='blacklist_tokens')
    op.drop_table('blacklist_tokens')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blacklist_tokens',
    sa.Column('jti', mysql.VARCHAR(length=500), nullable=False),
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('jti', 'blacklist_tokens', ['jti'], unique=True)
    op.drop_table('auth_tokens')
    # ### end Alembic commands ###
