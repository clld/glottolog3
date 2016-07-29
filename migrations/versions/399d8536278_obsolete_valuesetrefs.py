# coding=utf-8
"""obsolete valuesetrefs

Revision ID: 399d8536278
Revises: 21f6064e20a6
Create Date: 2016-01-28 08:50:57.143707

"""

# revision identifiers, used by Alembic.
revision = '399d8536278'
down_revision = '21f6064e20a6'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("DELETE FROM valuesetreference WHERE source_pk IS NULL")


def downgrade():
    pass
