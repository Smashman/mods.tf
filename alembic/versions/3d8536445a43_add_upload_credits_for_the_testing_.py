"""Add upload credits (For the testing period)

Revision ID: 3d8536445a43
Revises: 2ebc6e1081be
Create Date: 2014-08-03 23:22:58.636185

"""

# revision identifiers, used by Alembic.
revision = '3d8536445a43'
down_revision = '2ebc6e1081be'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('upload_credits', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'upload_credits')
    ### end Alembic commands ###
