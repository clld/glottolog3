# coding=utf-8
"""fix assoc tables

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

UNIQUE = [
    # clld
    ('contributioncontributor', ['contribution_pk', 'contributor_pk']),
    ('contributionreference', ['contribution_pk', 'source_pk']),
    ('editor', ['dataset_pk', 'contributor_pk']),
    ('languageidentifier', ['language_pk', 'identifier_pk']),
    ('languagesource', ['language_pk', 'source_pk']),
    ('sentencereference', ['sentence_pk', 'source_pk']),
    ('unitvalue', ['unit_pk', 'unitparameter_pk', 'unitdomainelement_pk']),  # ude_pk nullable
    ('value', ['valueset_pk', 'domainelement_pk']),  # de_pk nullable
    ('valuesentence', ['value_pk', 'sentence_pk']),
    ('valueset', ['language_pk', 'parameter_pk']),
    ('valuesetreference', ['valueset_pk', 'source_pk']),
    # glottolog3 (reorder)
    ('languoidcountry', ['languoid_pk', 'country_pk']),
    ('languoidmacroarea', ['languoid_pk', 'macroarea_pk']),
    ('refcountry', ['ref_pk', 'country_pk']),
    ('refdoctype', ['ref_pk', 'doctype_pk']),
    ('refmacroarea', ['ref_pk', 'macroarea_pk']),
    ('refprovider', ['ref_pk', 'provider_pk']),
]


def upgrade():
    conn = op.get_bind()

    def select_duplicate(tab, cols):
        cols = ', '.join(cols)
        return sa.text('SELECT %(cols)s, count(*) FROM %(tab)s '
            'GROUP BY %(cols)s HAVING count(*) > 1 ORDER BY %(cols)s' % locals(), conn)

    select_const = sa.text('SELECT name, definition FROM ('
        'SELECT c.conname AS name, pg_get_constraintdef(c.oid) AS definition, '
        'array(SELECT a.attname::text FROM unnest(c.conkey) AS n '
        'JOIN pg_attribute AS a ON a.attrelid = c.conrelid AND a.attnum = n '
        'ORDER BY a.attname) AS names '
        'FROM pg_constraint AS c WHERE c.contype = :type AND c.conrelid = '
        '(SELECT oid FROM pg_class AS t WHERE t.relname = :tab)) AS s '
        'WHERE s.names @> :cols AND s.names <@ :cols',
        conn).bindparams(type='u')

    duplicates = [(tab, cols, select_duplicate(tab, cols).execute().fetchall())
        for tab, cols in UNIQUE]
    violating = [(tab, cols, rows) for tab, cols, rows in duplicates if rows]
    if violating:
        for tab, cols, rows in violating:
            print 'violating %s UNIQUE(%s): %d' % (tab, ', '.join(cols), len(rows))
        raise RuntimeError

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

    raise NotImplementedError


def downgrade():
    pass
