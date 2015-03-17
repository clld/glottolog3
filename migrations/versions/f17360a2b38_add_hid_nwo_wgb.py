# coding=utf-8
"""add_hid_nwo_wgb

Revision ID: f17360a2b38
Revises: 4f8596e1d065
Create Date: 2015-03-17 10:16:22.747000

"""

# revision identifiers, used by Alembic.
revision = 'f17360a2b38'
down_revision = '4f8596e1d065'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    # nwo
    id, before, after, iso = 'nauo1235', 'NOCODE_Nauo', 'nwo', 'nwo'

    op.execute(sa.text('UPDATE language AS l SET updated = now() '
        'WHERE id = :id AND EXISTS (SELECT 1 FROM languoid '
        'WHERE pk = l.pk AND hid = :before)'
        ).bindparams(id=id, before=before))
    op.execute(sa.text('UPDATE languoid AS ll SET hid = :after '
        'WHERE hid = :before AND EXISTS (SELECT 1 FROM language '
        'WHERE pk = ll.pk AND id = :id)'
        ).bindparams(id=id, before=before, after=after))

    op.execute(sa.text('INSERT INTO identifier (created, updated, active, version, '
        'type, lang, name) '
        'SELECT now(), now(), true, 1, :type, :lang, :name '
        'WHERE NOT EXISTS (SELECT 1 FROM identifier '
        'WHERE type = :type AND lang = :lang AND name = :name)'
        ).bindparams(name=iso, type='iso639-3', lang='en'))
    op.execute(sa.text('INSERT INTO languageidentifier (created, updated, active, version, '
        'language_pk, identifier_pk) '
        'SELECT now(), now(), true, 1, '
        '(SELECT pk FROM language WHERE id = :id), '
        '(SELECT pk FROM identifier WHERE type = :type AND lang = :lang AND name = :name) '
        'WHERE NOT EXISTS (SELECT 1 FROM languageidentifier '
        'WHERE language_pk = (SELECT pk FROM language WHERE id = :id) '
        'AND identifier_pk = (SELECT pk FROM identifier '
        'WHERE type = :type AND lang = :lang AND name = :name))'
        ).bindparams(id=id, name=iso, type='iso639-3', lang='en'))

    # wgb
    id, name, hid, iso = 'waga1268', 'Wagawaga', 'wgb', 'wgb'

    op.execute(sa.text('INSERT INTO language (created, updated, active, version, '
        'polymorphic_type, jsondata, id, name) '
        'SELECT now(), now(), true, 1, :pm_type, :jsondata, :id, :name '
        'WHERE NOT EXISTS (SELECT 1 FROM language WHERE id = :id)'
        ).bindparams(id=id, name=name, pm_type='custom', jsondata='{}'))
    op.execute(sa.text('INSERT INTO languoid (pk, hid, level, status, '
        'child_family_count, child_language_count, child_dialect_count) '
        'SELECT (SELECT pk FROM language WHERE id = :id), '
        ':hid, :level, :status, 0, 0, 0 '
        'WHERE NOT EXISTS (SELECT 1 FROM languoid '
        'WHERE pk = (SELECT pk FROM language WHERE id = :id))'
        ).bindparams(id=id, hid=hid, level='language', status='established'))

    op.execute(sa.text('INSERT INTO identifier (created, updated, active, version, '
        'type, lang, description, name) '
        'SELECT now(), now(), true, 1, :type, :lang, :description, :name '
        'WHERE NOT EXISTS (SELECT 1 FROM identifier '
        'WHERE type = :type AND lang = :lang AND description = :description AND name = :name)'
        ).bindparams(name=name, type='name', lang='en', description='Glottolog'))
    op.execute(sa.text('INSERT INTO languageidentifier (created, updated, active, version, '
        'language_pk, identifier_pk) '
        'SELECT now(), now(), true, 1, '
        '(SELECT pk FROM language WHERE id = :id), '
        '(SELECT pk FROM identifier WHERE type = :type AND lang = :lang AND description = :description AND name = :name) '
        'WHERE NOT EXISTS (SELECT 1 FROM languageidentifier '
        'WHERE language_pk = (SELECT pk FROM language WHERE id = :id) '
        'AND identifier_pk = (SELECT pk FROM identifier '
        'WHERE type = :type AND lang = :lang AND description = :description AND name = :name))'
        ).bindparams(id=id, name=name, type='name', lang='en', description='Glottolog'))

    op.execute(sa.text('INSERT INTO identifier (created, updated, active, version, '
        'type, lang, name) '
        'SELECT now(), now(), true, 1, :type, :lang, :name '
        'WHERE NOT EXISTS (SELECT 1 FROM identifier '
        'WHERE type = :type AND lang = :lang AND name = :name)'
        ).bindparams(name=iso, type='iso639-3', lang='en'))
    op.execute(sa.text('INSERT INTO languageidentifier (created, updated, active, version, '
        'language_pk, identifier_pk) '
        'SELECT now(), now(), true, 1, '
        '(SELECT pk FROM language WHERE id = :id), '
        '(SELECT pk FROM identifier WHERE type = :type AND lang = :lang AND name = :name) '
        'WHERE NOT EXISTS (SELECT 1 FROM languageidentifier '
        'WHERE language_pk = (SELECT pk FROM language WHERE id = :id) '
        'AND identifier_pk = (SELECT pk FROM identifier '
        'WHERE type = :type AND lang = :lang AND name = :name))'
        ).bindparams(id=id, name=iso, type='iso639-3', lang='en'))


def downgrade():
    pass
