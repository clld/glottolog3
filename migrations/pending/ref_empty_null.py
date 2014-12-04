# coding=utf-8
"""ref empty null

Revision ID:
Revises:
Create Date:

"""

# revision identifiers, used by Alembic.
revision = ''
down_revision = ''

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()

    select_cols = sa.text('SELECT a.attname FROM pg_attribute AS a '
        'JOIN pg_class AS c ON a.attrelid = c.oid '
        'JOIN pg_type AS t ON a.atttypid = t.oid '
        'WHERE c.relname = :table AND t.typname = :type '
        'AND a.attnum > 0 AND NOT a.attnotnull', conn)

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
                print table, col, changed


def downgrade():
    pass
