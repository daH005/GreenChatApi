"""token > jti

Revision ID: 09853867d484
Revises: 146e8a89f614
Create Date: 2024-09-07 13:30:18.582302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '09853867d484'
down_revision: Union[str, None] = '146e8a89f614'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('blacklist_tokens', sa.Column('jti', sa.String(length=500), nullable=False))
    op.drop_index('token', table_name='blacklist_tokens')
    op.create_unique_constraint(None, 'blacklist_tokens', ['jti'])
    op.drop_column('blacklist_tokens', 'token')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('blacklist_tokens', sa.Column('token', mysql.VARCHAR(length=500), nullable=False))
    op.drop_constraint(None, 'blacklist_tokens', type_='unique')
    op.create_index('token', 'blacklist_tokens', ['token'], unique=False)
    op.drop_column('blacklist_tokens', 'jti')
    # ### end Alembic commands ###