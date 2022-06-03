"""empty message

Revision ID: 90efb5979fe1
Revises: baf5f173a6b8
Create Date: 2022-06-01 21:39:01.453895

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90efb5979fe1'
down_revision = 'baf5f173a6b8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'phone')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('phone', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
