"""Add author order

Revision ID: 284495b61141
Revises: 28beb21ba379
Create Date: 2014-07-28 17:57:20.578971

"""

# revision identifiers, used by Alembic.
revision = '284495b61141'
down_revision = '28beb21ba379'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('mod_author', sa.Column('order', sa.Integer(), nullable=False))
    pass


def downgrade():
    op.drop_column('mod_author', 'order')
    pass
