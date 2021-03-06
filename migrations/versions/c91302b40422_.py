"""empty message

Revision ID: c91302b40422
Revises: 850ae7cf0e84
Create Date: 2020-05-14 12:47:15.676004

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c91302b40422'
down_revision = '850ae7cf0e84'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('reviews', 'rating',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('reviews', 'review',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'user_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'user_name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('reviews', 'review',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('reviews', 'rating',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
