# coding=utf-8
"""add columns for cached associations

Revision ID: 3cd6bf1141c8
Revises: 3f325e2fa551
Create Date: 2013-09-17 15:54:45.505746

"""

# revision identifiers, used by Alembic.
revision = '3cd6bf1141c8'
down_revision = '3f325e2fa551'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('ref', sa.Column('providers_str', sa.Unicode))
    op.add_column('ref', sa.Column('doctypes_str', sa.Unicode))


def downgrade():
    op.drop_column('ref', 'providers_str')
    op.drop_column('ref', 'doctypes_str')
