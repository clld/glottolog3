# coding=utf-8
"""fix providers_str

Revision ID: 53f4e74ce460
Revises: 176e169bf976
Create Date: 2014-06-30 19:27:16.307718

"""

# revision identifiers, used by Alembic.
revision = '53f4e74ce460'
down_revision = '176e169bf976'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute(
        "update ref set providers_str = 'hh' where providers_str = 'glottolog20121, hh'")


def downgrade():
    pass
