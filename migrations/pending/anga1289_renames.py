# coding=utf-8
"""anga1289 renames

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

GCODE_OLD_NEW = [
    ('nort3145', 'Northeast Angan', 'Wojokesic'),
    ('sout3130', 'Southwest Angan', 'Ankave-Tainae-Akoye'),
]


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
