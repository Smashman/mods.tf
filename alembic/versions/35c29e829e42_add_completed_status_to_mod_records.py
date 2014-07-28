"""Add completed status to mod records

Revision ID: 35c29e829e42
Revises: 284495b61141
Create Date: 2014-07-28 23:08:26.708142

"""

# revision identifiers, used by Alembic.
revision = '35c29e829e42'
down_revision = '284495b61141'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('mods', sa.Column('completed', sa.Boolean(), nullable=False))
    pass


def downgrade():
    op.drop_column('mods', 'app')
    pass
