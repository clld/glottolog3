# coding=utf-8
"""moseley as name provider

Revision ID: baf6409f1f7
Revises: 184b209609c4
Create Date: 2014-06-20 10:53:49.558473

"""

# revision identifiers, used by Alembic.
revision = 'baf6409f1f7'
down_revision = '184b209609c4'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    for pair in [
        ('WALS other', 'Bibiko'),
        ('Moseley & Asher (1994)', 'Mosely & Asher (1994)'),
    ]:
        op.execute(
            "update identifier set description = '%s' where description = '%s'" % pair)


def downgrade():
    pass
