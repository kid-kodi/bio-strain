"""empty message

Revision ID: b360758b44e6
Revises: 89582dca29df
Create Date: 2019-01-30 11:37:11.000631

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b360758b44e6'
down_revision = '89582dca29df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('disease',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['disease.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_disease_created_at'), 'disease', ['created_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_disease_created_at'), table_name='disease')
    op.drop_table('disease')
    # ### end Alembic commands ###
