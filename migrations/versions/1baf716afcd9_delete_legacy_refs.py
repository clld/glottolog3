# coding=utf-8
"""delete legacy refs

Revision ID: 1baf716afcd9
Revises: 7a787c138e
Create Date: 2014-12-08 18:23:02.156000

"""

# revision identifiers, used by Alembic.
revision = '1baf716afcd9'
down_revision = '7a787c138e'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()

    select_referencing = sa.text('SELECT s.relname AS tab, sa.attname AS col '
        'FROM pg_constraint AS c '
        'JOIN pg_class AS s ON c.conrelid = s.oid '
        'JOIN pg_attribute AS sa ON sa.attrelid = s.oid AND sa.attnum = ANY(c.conkey) '
        'JOIN pg_class AS t ON c.confrelid = t.oid '
        'JOIN pg_attribute AS ta ON ta.attrelid = t.oid AND ta.attnum = ANY(c.confkey) '
        'WHERE c.contype = :type AND t.relname = :tab AND ta.attname = :col '
        'ORDER BY tab, col', conn).bindparams(type='f')

    delete_referencing = ('DELETE FROM %(rtab)s WHERE EXISTS (SELECT 1 '
        'FROM source JOIN ref ON source.pk = ref.pk '
        'JOIN legacyref ON legacyref.id = source.id '
        'WHERE %(rtab)s.%(rcol)s = %(tab)s.%(col)s)')

    delete = ('DELETE FROM %(tab)s AS d WHERE EXISTS (SELECT 1 '
        'FROM source JOIN legacyref ON legacyref.id = source.id '
        'WHERE d.pk = source.pk)')

    tab_col = [('ref', 'pk'), ('source', 'pk')]

    for tab, col in tab_col:
        for rtab, rcol in select_referencing.execute(tab=tab, col=col):
            if (rtab, rcol) not in tab_col:
                conn.execute(delete_referencing % locals())
        conn.execute(delete % {'tab': tab})


def downgrade():
    pass
