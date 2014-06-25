# coding=utf-8
"""reorder editors

Revision ID: 176e169bf976
Revises: 3f0d8ed62bf2
Create Date: 2014-06-25 16:10:34.282027

"""

# revision identifiers, used by Alembic.
revision = '176e169bf976'
down_revision = '3f0d8ed62bf2'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    for old, new in [(1, 5), (2, 1), (3, 2), (4, 3), (5, 4)]:
        op.execute('update editor set ord = %s where ord = %s' % (new, old))


def downgrade():
    pass
