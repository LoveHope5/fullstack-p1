"""empty message

Revision ID: 1f484eb18de6
Revises: e68e3fdbd1e9
Create Date: 2022-06-03 04:42:33.133926

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f484eb18de6'
down_revision = 'e68e3fdbd1e9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'available_from')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('available_from', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
