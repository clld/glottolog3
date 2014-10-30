# coding=utf-8
"""fix identifier delimited

Revision ID: 209d7444dee3
Revises: 316e1bd8f046
Create Date: 2014-10-30 10:55:35.915000

"""

# revision identifiers, used by Alembic.

revision = '209d7444dee3'
down_revision = '316e1bd8f046'

import datetime

from alembic import op
import sqlalchemy as sa

DELIMITERS = ['; ', ' / ', ' = ']


def upgrade():
    conn = op.get_bind()

    select_delimited = sa.text(
        'SELECT iii.pk, iii.id, iii.type, iii.description, iii.lang, iii.name, iii.names, iii.other, '
            'array_agg(li.language_pk ORDER BY li.language_pk) AS languages '
        'FROM ('
            'SELECT ii.pk, ii.id, ii.type, ii.description, ii.lang, ii.name, '
                'array_agg(ii.split ORDER BY n) as names ,'
                'array_agg(ii.other ORDER BY n) as other '
            'FROM ('
                'SELECT i.pk, i.id, i.type, i.description, i.lang, i.name, '
                    'i.split, row_number() OVER () as n, '
                    'EXISTS (SELECT 1 FROM identifier '
                        'WHERE type = i.type AND description = i.description '
                        'AND lang = i.lang AND name = i.split) AS other '
                'FROM ('
                    'SELECT pk, id, type, description, lang, name, '
                        'trim(regexp_split_to_table(name, :delim)) AS split '
                    'FROM identifier WHERE name ~ :delim '
                ') AS i '
            ') AS ii WHERE split != \'\' '
            'GROUP BY ii.pk, ii.id, ii.type, ii.description, ii.lang, ii.name '
        ') as iii '
        'JOIN languageidentifier AS li ON li.identifier_pk = iii.pk '
        'GROUP BY iii.pk, iii.id, iii.type, iii.description, iii.lang, iii.name, iii.names, iii.other '
        'ORDER BY iii.name', conn)

    delete_ident = sa.text('DELETE FROM identifier WHERE pk = :pk', conn)
    delete_lang_ident = sa.text('DELETE FROM languageidentifier '
        'WHERE identifier_pk = :identifier_pk '
        'AND language_pk = ANY(:languages)', conn)

    update_lang = sa.text('UPDATE language SET updated = now(), name = :newname '
        'WHERE name = :oldname and pk = ANY(:languages)', conn)

    insert_ident = sa.text('INSERT INTO identifier '
        '(created, updated, active, version, id, type, description, lang, name) '
        'VALUES (now(), now(), true, 1, :id, :type, :description, :lang, :name) '
        'RETURNING (pk)', conn)
    insert_lang_ident = sa.text('INSERT INTO languageidentifier '
        '(created, updated, active, version, language_pk, identifier_pk) '
        'VALUES (now(), now(), true, 1, :language_pk, :identifier_pk)', conn)

    # prevent ill split
    sa.text('UPDATE identifier SET updated = now(), '
        'name = :after WHERE name = :before', conn)\
        .execute(before='Milang (Damu = Bori = Adi)', after='Milang (Damu)')
    sa.text('UPDATE language SET updated = now(), '
        'name = :after WHERE name = :before', conn)\
        .execute(before='Milang (Damu = Bori = Adi)', after='Milang (Damu)')
    

    for delim in DELIMITERS:
        target = select_delimited.execute(delim=delim)
        for old, id, type, description, lang, name, names, others, languages in target:
            delete_lang_ident.execute(identifier_pk=old, languages=languages)
            delete_ident.execute(pk=old)

            if type == 'name' and description == 'Glottolog':
                update_lang.execute(oldname=name, newname=names[0], languages=languages)

            for name, other in zip(names, others):
                if other:
                    continue
                new = insert_ident.scalar(id=id, type=type,
                    description=description, lang=lang, name=name)
                for language_pk in languages:
                    insert_lang_ident.execute(language_pk=language_pk,
                        identifier_pk=new)


def downgrade():
    pass
