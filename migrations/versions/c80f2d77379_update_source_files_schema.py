# coding=utf-8
"""update source_files schema

Revision ID: c80f2d77379
Revises: 56d1bff8c07d
Create Date: 2014-06-18 16:08:13.447447

"""

# revision identifiers, used by Alembic.
revision = 'c80f2d77379'
down_revision = '56d1bff8c07d'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('source_files', sa.Column('id', sa.String, unique=True))
    op.add_column('source_files', sa.Column('mime_type', sa.String))
    op.add_column('source_files', sa.Column('description', sa.Unicode))
    op.add_column('source_files', sa.Column('markup_description', sa.Unicode))


def downgrade():
    op.drop_column('source_files', 'id')
    op.drop_column('source_files', 'mime_type')
    op.drop_column('source_files', 'description')
    op.drop_column('source_files', 'markup_description')
