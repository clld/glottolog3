# coding=utf-8
"""name changes

Revision ID: 4132cc50d511
Revises: 30549d803590
Create Date: 2014-12-19 10:07:46.160000

"""

# revision identifiers, used by Alembic.
revision = '4132cc50d511'
down_revision = '30549d803590'

import datetime

from alembic import op
import sqlalchemy as sa

GCODE_OLD_NEW = [
    ('huaa1248', '=/Hua', 'Amkoe'),
    ('kxau1241', "=/Kx'au//'ein", "Kx'ao'ae"),
    ('anii1246', '//Ani', 'Ani'),
    ('gana1274', '//Gana', 'Gana'),
    ('gwii1239', '/Gwi', 'Gwi'),
    ('haio1238', 'Hai//om', 'Haiom'),
    ('juho1239', "Ju/'hoan", "Ju'hoan"),
    ('nuuu1241', 'N/u', 'Neng'),
    ('xamm1241', '/Xam', 'Kham'),
    ('xegw1238', '//Xegwi', 'Xegwi'),
    ('xooo1239', '!Xoo', 'Xoon'),
    ('oung1238', '!O!ung', 'Sekele'),
    ('kwii1241', '!Kwi', 'Kwi')]


def upgrade():
    update_name = sa.text('UPDATE language SET updated = now(), '
        'name = :after WHERE id = :id AND name = :before')

    insert_ident = sa.text('INSERT INTO identifier '
        '(created, updated, active, version, type, description, lang, name) '
        'SELECT now(), now(), true, 1, :type, :description, :lang, :name '
        'WHERE NOT EXISTS (SELECT 1 FROM identifier WHERE type = :type '
        'AND description = :description AND lang = :lang AND name = :name)'
        ).bindparams(type='name', description='Glottolog', lang='en')

    insert_lang_ident = sa.text('INSERT INTO languageidentifier '
        '(created, updated, active, version, language_pk, identifier_pk) '
        'SELECT now(), now(), true, 1, '
        '(SELECT pk FROM language WHERE id = :id), '
        '(SELECT pk FROM identifier WHERE type = :type '
        'AND description = :description AND lang = :lang AND name = :name) '
        'WHERE NOT EXISTS (SELECT 1 FROM languageidentifier '
        'WHERE language_pk = (SELECT pk FROM language WHERE id = :id) '
        'AND identifier_pk = (SELECT pk FROM identifier WHERE type = :type '
        'AND description = :description AND lang = :lang AND name = :name))'
        ).bindparams(type='name', description='Glottolog', lang='en')

    for id, before, after in GCODE_OLD_NEW:
        op.execute(update_name.bindparams(id=id, before=before, after=after))
        op.execute(insert_ident.bindparams(name=after))
        op.execute(insert_lang_ident.bindparams(id=id, name=after))


def downgrade():
    pass
