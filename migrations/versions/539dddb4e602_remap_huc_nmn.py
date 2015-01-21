# coding=utf-8
"""remap huc nmn

Revision ID: 539dddb4e602
Revises: 453449671748
Create Date: 2015-01-21 11:00:43.943000

"""

# revision identifiers, used by Alembic.
revision = '539dddb4e602'
down_revision = '453449671748'

import datetime

from alembic import op
import sqlalchemy as sa

LANGS = [
    ('xooo1239', 'nmn', 'NOCODE_West-Taa'),
    ('huaa1248', 'huc', 'nmn'),
    ('hoaa1235', 'NOCODE_Hoa', 'huc'),
]


def upgrade():
    def update_hid(id, before, after):
        yield sa.text('UPDATE language AS l SET updated = now() '
            'WHERE id = :id AND EXISTS (SELECT 1 FROM languoid '
            'WHERE pk = l.pk AND hid = :before)'
            ).bindparams(id=id, before=before)
        yield sa.text('UPDATE languoid AS ll SET hid = :after '
            'WHERE hid = :before AND EXISTS (SELECT 1 FROM language '
            'WHERE pk = ll.pk AND id = :id)'
            ).bindparams(id=id, before=before, after=after)

    def delete_iso(id, name, type='iso639-3', lang='en'):
        yield sa.text('DELETE FROM languageidentifier AS li '
            'WHERE EXISTS (SELECT 1 FROM language WHERE pk = li.language_pk '
            'AND id = :id) '
            'AND EXISTS (SELECT 1 FROM identifier WHERE pk = li.identifier_pk '
            'AND type = :type AND lang = :lang AND name = :name)'
            ).bindparams(id=id, name=name, type=type, lang=lang)
        yield sa.text('DELETE FROM identifier AS i '
            'WHERE type = :type AND lang = :lang AND name = :name '
            'AND NOT EXISTS (SELECT 1 FROM languageidentifier '
            'WHERE identifier_pk = i.pk)'
            ).bindparams(name=name, type=type, lang=lang)

    def insert_iso(id, name, type='iso639-3', lang='en'):
        yield sa.text('INSERT INTO identifier '
            '(created, updated, active, version, type, lang, name) '
            'SELECT now(), now(), true, 1, :type, :lang, :name '
            'WHERE NOT EXISTS (SELECT 1 FROM identifier WHERE type = :type '
            'AND lang = :lang AND name = :name)'
            ).bindparams(name=name, type=type, lang=lang)
        yield sa.text('INSERT INTO languageidentifier '
            '(created, updated, active, version, language_pk, identifier_pk) '
            'SELECT now(), now(), true, 1, '
            '(SELECT pk FROM language WHERE id = :id), '
            '(SELECT pk FROM identifier WHERE type = :type AND lang = :lang '
            'AND name = :name) '
            'WHERE NOT EXISTS (SELECT 1 FROM languageidentifier '
            'WHERE language_pk = (SELECT pk FROM language WHERE id = :id) '
            'AND identifier_pk = (SELECT pk FROM identifier WHERE type = :type '
            'AND lang = :lang AND name = :name))'
            ).bindparams(id=id, name=name, type=type, lang=lang)

    for id, before, after in LANGS:
        for query in update_hid(id, before, after):
            op.execute(query)
        if len(before) == 3:
            for query in delete_iso(id, before):
                op.execute(query)
        if len(after) == 3:
            for query in insert_iso(id, after):
                op.execute(query)


def downgrade():
    pass
