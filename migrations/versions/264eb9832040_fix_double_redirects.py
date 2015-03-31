# coding=utf-8
"""fix double redirects

Revision ID: 264eb9832040
Revises: 1e83591108ca
Create Date: 2015-03-31 13:10:50.531000

"""

# revision identifiers, used by Alembic.
revision = '264eb9832040'
down_revision = '1e83591108ca'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()
    trans_closure = sa.text("""WITH RECURSIVE r(key, steps, dst) AS (
        SELECT c.key, 1, NULLIF(c.value, '__gone__') AS dst
        FROM config AS c WHERE c.value != '__gone__'
        UNION ALL SELECT cc.key, r.steps + 1, r.dst
        FROM config AS cc JOIN r ON format('__Source_%s__', cc.value) = r.key)
    SELECT key, array_agg(dst ORDER BY steps) AS path
    FROM r GROUP BY key HAVING count(*) > 1 ORDER BY key""", conn)
    update_conf = sa.text('UPDATE config SET updated = now(), value = :after '
        'WHERE key = :key AND value = :before', conn)
    for key, path in trans_closure.execute():
        for before in path[:-1]:
            update_conf.execute(key=key, before=before, after=path[-1])


def downgrade():
    pass
