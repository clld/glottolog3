# coding=utf-8
"""sync source pk with id

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
    update_source_pks([
        {'before': 320754, 'after': 500001},
        {'before': 320755, 'after': 500002}])
    # TODO: update source pk sequence
    

def downgrade():
    update_source_pks([
        {'after': 320754, 'before': 500001},
        {'after': 320755, 'before': 500002}])


def update_source_pks(before_after):
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

    conn = op.get_bind()
    fks = conn.execute(select_fks).fetchall()
    drop, add = zip(*map(drop_add_fk, fks))
    
    conn.execute(';\n'.join(drop))
    conn.execute(update_source, before_after)
    for names in fks:
        conn.execute(sa.text(update_other % names), before_after)
    conn.execute(';\n'.join(add))
