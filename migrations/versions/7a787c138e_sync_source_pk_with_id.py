# coding=utf-8
"""sync source pk with id

Revision ID: 7a787c138e
Revises: 185b48316200
Create Date: 2014-12-08 17:08:56.307000

"""

# revision identifiers, used by Alembic.
revision = '7a787c138e'
down_revision = '185b48316200'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade(verbose=True):
    conn = op.get_bind()

    select_ba = sa.text('SELECT s.pk AS before, s.id::int AS after '
        'FROM source AS s WHERE s.pk != s.id::int '
        'AND NOT EXISTS (SELECT 1 FROM source WHERE pk = s.id::int) '
        'ORDER BY s.id::int', conn)

    set_sequence = sa.text("""SELECT setval('source_pk_seq', max(x))
        FROM unnest(array[(SELECT coalesce(max(pk), 0) FROM source), :minimum])
        AS x""", conn)

    before_after = select_ba.execute().fetchall()
    if verbose:
        from itertools import groupby
        def groupkey(key):
            i, (b, a) = key
            return i - b
        def consecutive(ba):
            for k, g in groupby(enumerate(ba), groupkey):
                group = [ba for i, ba in g]
                yield group[0], group[-1]
        print(list(consecutive(before_after)))
            
    update_source_pks(conn, before_after)

    set_sequence.scalar(minimum=510000)
    

def downgrade():
    pass


def update_source_pks(conn, before_after):
    select_fks = sa.text('SELECT c.conname AS const, '
            's.relname AS stab, sa.attname AS scol, '
            't.relname AS ttab, ta.attname AS tcol '
        'FROM pg_constraint AS c '
        'JOIN pg_class AS s ON c.conrelid = s.oid '
        'JOIN pg_attribute AS sa ON sa.attrelid = s.oid AND sa.attnum = ANY(c.conkey) '
        'JOIN pg_class AS t ON c.confrelid = t.oid '
        'JOIN pg_attribute AS ta ON ta.attrelid = t.oid AND ta.attnum = ANY(c.confkey) '
        'WHERE c.contype = :type AND (t.relname, ta.attname) IN :tabcols '
        'ORDER BY ttab, tcol, stab, scol',
        ).bindparams(type='f', tabcols=(('source', 'pk'), ('ref', 'pk')))

    def drop_add_fk(names):
        yield 'ALTER TABLE %(stab)s DROP CONSTRAINT %(const)s' % names
        yield ('ALTER TABLE %(stab)s ADD CONSTRAINT %(const)s '
            'FOREIGN KEY (%(scol)s) REFERENCES %(ttab)s (%(tcol)s)' % names)
    
    update_source = sa.text('UPDATE source SET pk = :after WHERE pk = :before')
    update_other = 'UPDATE %(stab)s SET %(scol)s = :after WHERE %(scol)s = :before'

    fks = conn.execute(select_fks).fetchall()
    drop, add = zip(*map(drop_add_fk, fks))
    
    conn.execute(';\n'.join(drop))
    conn.execute(update_source, before_after)
    for names in fks:
        conn.execute(sa.text(update_other % names), before_after)
    conn.execute(';\n'.join(add))
