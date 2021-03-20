"""empty message

Revision ID: e8b1dfbabe3d
Revises: e1e983403ad1
Create Date: 2020-03-06 11:36:21.099368

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8b1dfbabe3d'
down_revision = 'e1e983403ad1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reservations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('reserve_name', sa.String(length=500), nullable=True),
    sa.Column('reserve_time', sa.DateTime(), nullable=True),
    sa.Column('reserve_book_name', sa.String(length=500), nullable=True),
    sa.Column('reserve_status', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reservations')
    # ### end Alembic commands ###