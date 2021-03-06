"""empty message

Revision ID: d32f11c84c7e
Revises: 
Create Date: 2022-02-12 04:09:55.195366

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd32f11c84c7e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=32), nullable=False),
    sa.Column('role', sa.Enum('root', 'admin', 'viewer', 'banned', name='adminrolesenum'), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('password', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('errors_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('url', sa.String(length=70), nullable=False),
    sa.Column('status_code', sa.Integer(), nullable=True),
    sa.Column('story_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('instagram_cookies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cookie', sa.PickleType(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stories_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('stage', sa.Enum('received', 'uploading', 'uploaded', 'failed', name='storystagesenum'), nullable=False),
    sa.Column('error_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stories_log')
    op.drop_table('instagram_cookies')
    op.drop_table('errors_log')
    op.drop_table('admins')
    # ### end Alembic commands ###
