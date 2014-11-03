# coding=utf-8
"""strip whitespace

Revision ID: 5a78dba481df
Revises: 2a0e1708e80
Create Date: 2014-11-03 11:10:44.089000

"""

# revision identifiers, used by Alembic.

revision = '5a78dba481df'
down_revision = '2a0e1708e80'

import datetime
import json

from alembic import op
import sqlalchemy as sa

TABLE_COL_UPDATED = [
    ('identifier', 'name', True),
    ('language', 'name', True),
    ('macroarea', 'description', True),
    ('provider', 'name', True),
    ('ref', 'normalizedauthorstring', False),
    ('ref', 'normalizededitorstring', False),
    ('source', 'author', True),
    ('source', 'editor', True),
    ('source', 'name', True)
]

QUERIES = [
    ('UPDATE %(table)s SET '
        '%(col)s = trim(%(col)s) WHERE %(col)s != trim(%(col)s)'),
    ('UPDATE %(table)s SET updated = now(), '
        '%(col)s = trim(%(col)s) WHERE %(col)s != trim(%(col)s)'),
]
    

def upgrade():
    for table, col, updated in TABLE_COL_UPDATED:
        update_trim = QUERIES[updated] % {'table': table, 'col': col}
        op.execute(update_trim)


def downgrade():
    pass
