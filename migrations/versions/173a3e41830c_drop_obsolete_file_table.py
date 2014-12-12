# coding=utf-8
"""drop obsolete file table

Revision ID: 173a3e41830c
Revises: 37a388e0c809
Create Date: 2014-12-12 12:17:23.362000

"""

# revision identifiers, used by Alembic.
revision = '173a3e41830c'
down_revision = '37a388e0c809'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()

    has_table = sa.text('SELECT EXISTS (SELECT 1 '
        'FROM information_schema.tables WHERE table_name = :name)', conn)

    select_fks = sa.text('SELECT c.conname AS const, '
            's.relname AS stab, sa.attname AS scol, '
            't.relname AS ttab, ta.attname AS tcol '
        'FROM pg_constraint AS c '
        'JOIN pg_class AS s ON c.conrelid = s.oid '
        'JOIN pg_attribute AS sa ON sa.attrelid = s.oid AND sa.attnum = ANY(c.conkey) '
        'JOIN pg_class AS t ON c.confrelid = t.oid '
        'JOIN pg_attribute AS ta ON ta.attrelid = t.oid AND ta.attnum = ANY(c.confkey) '
        'WHERE c.contype = :type AND t.relname = :ttab '
        'ORDER BY ttab, tcol, stab, scol', conn
        ).bindparams(type='f')

    if has_table.scalar(name='file'):
        for const, stab, scol, ttab, tcol in select_fks.execute(ttab='file'):
            op.drop_column(stab, scol)
            op.drop_column('%s_history' % stab, scol)
        op.drop_table('file')


def downgrade():
    pass
