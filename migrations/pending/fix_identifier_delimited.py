# coding=utf-8
"""fix identifier delimited

Revision ID: 
Revises: 
Create Date: 2014-10-24 10:59:01.044000

"""

# revision identifiers, used by Alembic.

revision = ''
down_revision = ''

import datetime

from alembic import op
import sqlalchemy as sa

DELIMITERS = [
    '; ',
    ' [/=] ',
]


def upgrade():
    conn = op.get_bind()

    select_delimited = sa.text(
        'SELECT iii.pk, iii.type, iii.description, iii.lang, iii.names, iii.others, '
            'array_agg(li.language_pk ORDER BY li.language_pk) AS languages '
        'FROM ('
            'SELECT ii.pk, ii.type, ii.description, ii.lang, '
                'array_agg(ii.split ORDER BY split) as names ,'
                'array_agg(ii.other ORDER BY split) as others '
            'FROM ('
                'SELECT i.pk, i.type, i.description, i.lang, i.split, '
                    'EXISTS (SELECT 1 FROM identifier '
                        'WHERE type = i.type AND description = i.description '
                        'AND lang = i.lang AND name = i.split) AS other '
                'FROM ('
                    'SELECT pk, type, description, lang, '
                        'trim(regexp_split_to_table(name, :delim)) AS split '
                    'FROM identifier WHERE name ~ :delim '
                ') AS i '
            ') AS ii '
            'GROUP BY ii.pk, ii.type, ii.description, ii.lang '
        ') as iii '
        'JOIN languageidentifier AS li ON li.identifier_pk = iii.pk '
        'GROUP BY iii.pk, iii.type, iii.description, iii.lang, iii.names, iii.others '
        'ORDER BY iii.pk', conn)

    delete_ident = sa.text('DELETE FROM identifier WHERE pk = :pk', conn)
    delete_lang_ident = sa.text('DELETE FROM languageidentifier '
        'WHERE identifier_pk = :identifier_pk '
        'AND language_pk = ANY(:languages)', conn)

    insert_ident = sa.text('INSERT INTO identifier '
        '(created, updated, active, version, type, description, lang, name) '
        'VALUES (now(), now(), true, 1, :type, :description, :lang, :name) '
        'RETURNING (pk)', conn)
    insert_lang_ident = sa.text('INSERT INTO languageidentifier '
        '(created, updated, active, version, language_pk, identifier_pk) '
        'VALUES (now(), now(), true, 1, :language_pk, :identifier_pk)', conn)

    for delim in DELIMITERS:
        target = select_delimited.execute(delim=delim)
        for old, type, description, lang, names, others, languages in target:
            delete_lang_ident.execute(identifier_pk=old, languages=languages)
            delete_ident.execute(pk=old)

            for name, other in zip(names, others):
                if other:
                    continue
                new = insert_ident.scalar(type=type, description=description,
                    lang=lang, name=name)
                for language_pk in languages:
                    insert_lang_ident.execute(language_pk=language_pk,
                        identifier_pk=new)


def downgrade():
    pass
