"""Add forgotten 'image_inventory' field

Revision ID: 3642ec8d5d7c
Revises: 4109faaa8328
Create Date: 2014-07-08 21:37:19.250280

"""

# revision identifiers, used by Alembic.
revision = '3642ec8d5d7c'
down_revision = '4109faaa8328'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tf2_schema', sa.Column('image_inventory', sa.String(length=256), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tf2_schema', 'image_inventory')
    ### end Alembic commands ###