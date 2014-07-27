"""Modify mod columns

Revision ID: 30f34c437dbc
Revises: 347d18296575
Create Date: 2014-07-27 02:20:58.091094

"""

# revision identifiers, used by Alembic.
revision = '30f34c437dbc'
down_revision = '347d18296575'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mods', sa.Column('app', sa.Integer(), nullable=True))
    op.drop_column('mods', 'split_class')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mods', sa.Column('split_class', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.drop_column('mods', 'app')
    ### end Alembic commands ###
