# coding=utf-8
"""fix assoc tables

Revision ID: 2793805922ab
Revises: 3d8925dd5250
Create Date: 2015-04-27 11:47:50.228000

"""

# revision identifiers, used by Alembic.
revision = '2793805922ab'
down_revision = '3d8925dd5250'

import datetime

from alembic import op
import sqlalchemy as sa

UNIQUE_NULL = [
    ('languoidcountry', ['languoid_pk', 'country_pk'], []),
    ('languoidmacroarea', ['languoid_pk', 'macroarea_pk'], []),
    ('refcountry', ['ref_pk', 'country_pk'], []),
    ('refdoctype', ['ref_pk', 'doctype_pk'], []),
    ('refmacroarea', ['ref_pk', 'macroarea_pk'], []),
    ('refprovider', ['ref_pk', 'provider_pk'], []),
]

UNIQUE = [(tab, cols) for tab, cols, nullable in UNIQUE_NULL]
NOTNULL = [(tab, [c for c in cols if c not in nullable]) for tab, cols, nullable in UNIQUE_NULL]


def upgrade():
    conn = op.get_bind()

    def select_null(tab, cols):
        condition = ' OR '.join('%s IS NULL' % c for c in cols)
        return sa.text('SELECT * FROM %(tab)s WHERE %(condition)s' % locals(), conn)

    nulls = [(tab, cols, select_null(tab, cols).execute().fetchall())
        for tab, cols in NOTNULL]
    violating = [(tab, cols) for tab, cols, rows in nulls if rows]
    if violating:
        for tab, cols, rows in violating:
            print('violating %s NOT NULL(%s): %d' % (tab, ', '.join(cols), len(rows)))
        raise RuntimeError

    def select_duplicate(tab, cols):
        cols = ', '.join(cols)
        return sa.text('SELECT %(cols)s, count(*) FROM %(tab)s '
            'GROUP BY %(cols)s HAVING count(*) > 1 ORDER BY %(cols)s' % locals(), conn)

    duplicates = [(tab, cols, select_duplicate(tab, cols).execute().fetchall())
        for tab, cols in UNIQUE]
    violating = [(tab, cols, rows) for tab, cols, rows in duplicates if rows]
    if violating:
        for tab, cols, rows in violating:
            print('violating %s UNIQUE(%s): %d' % (tab, ', '.join(cols), len(rows)))
        raise RuntimeError

    select_nullable = sa.text('SELECT attname FROM pg_attribute '
        'WHERE attrelid = (SELECT oid FROM pg_class WHERE relname = :tab) '
        'AND NOT attnotnull AND attname = ANY(:cols) ORDER BY attnum', conn)

    select_const = sa.text('SELECT name, definition FROM ('
        'SELECT c.conname AS name, pg_get_constraintdef(c.oid) AS definition, '
        'array(SELECT a.attname::text FROM unnest(c.conkey) AS n '
        'JOIN pg_attribute AS a ON a.attrelid = c.conrelid AND a.attnum = n '
        'ORDER BY a.attname) AS names '
        'FROM pg_constraint AS c WHERE c.contype = :type AND c.conrelid = '
        '(SELECT oid FROM pg_class AS t WHERE t.relname = :tab)) AS s '
        'WHERE s.names @> :cols AND s.names <@ :cols',
        conn).bindparams(type='u')

    for tab, cols in NOTNULL:
        for col, in select_nullable.execute(tab=tab, cols=cols).fetchall():
            op.alter_column(tab, col, nullable=False)

    for tab, cols in UNIQUE:
        matching = select_const.execute(tab=tab, cols=cols).fetchall()
        if matching:
            assert len(matching) == 1
            name, definition = matching[0]
            if definition == 'UNIQUE (%s)' % ', '.join(cols):
                continue
            op.drop_constraint(name, tab)
        name = '%s_%s_key' % (tab, '_'.join(cols))
        op.create_unique_constraint(name, tab, cols)


def downgrade():
    pass
