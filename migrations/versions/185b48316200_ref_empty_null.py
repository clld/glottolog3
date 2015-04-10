# coding=utf-8
"""ref empty null

Revision ID: 185b48316200
Revises: 4b89d69d005c
Create Date: 2014-12-08 12:56:45.261000

"""

# revision identifiers, used by Alembic.
revision = '185b48316200'
down_revision = '4b89d69d005c'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade(verbose=True):
    conn = op.get_bind()

    select_cols = sa.text('SELECT a.attname FROM pg_attribute AS a '
        'JOIN pg_class AS c ON a.attrelid = c.oid '
        'JOIN pg_type AS t ON a.atttypid = t.oid '
        'WHERE c.relname = :table AND t.typname = :type '
        'AND a.attnum > 0 AND NOT a.attnotnull '
        'ORDER BY a.attnum', conn)

    def exists_empty(table, col):
        query = "SELECT EXISTS (SELECT 1 FROM %s WHERE %s = '')" % (table, col)
        return sa.text(query , conn)

    def nullify_empty(table, col):
        query = "UPDATE %s SET %s = NULL WHERE %s = ''" % (table, col, col)
        return sa.text(query, conn)

    for table in ['source', 'ref']:
        for col, in select_cols.execute(table=table, type='varchar'):
            if exists_empty(table, col).scalar():
                changed = nullify_empty(table, col).execute().rowcount
                if verbose:
                    print('%s.%s\t%d' % (table, col, changed))


def downgrade():
    pass
