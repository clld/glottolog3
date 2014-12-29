# coding=utf-8
"""fix missing name identifiers

Revision ID: f4b1d23d113
Revises: 4132cc50d511
Create Date: 2014-12-27 23:00:16.753000

"""

# revision identifiers, used by Alembic.
revision = 'f4b1d23d113'
down_revision = '4132cc50d511'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    insert_ident = sa.text('INSERT INTO identifier (created, updated, active, version, '
        'type, lang, description, name) '
        'SELECT now(), now(), true, 1, :type, :lang, :description, :name '
        'WHERE NOT EXISTS (SELECT 1 FROM identifier '
        'WHERE type = :type AND lang = :lang AND description = :description '
        'AND name = :name)').bindparams(type='name', lang='en', description='Glottolog')
    insert_lang_ident = sa.text('INSERT INTO languageidentifier (created, updated, active, version, '
        'language_pk, identifier_pk) '
        'SELECT now(), now(), true, 1, '
        '(SELECT pk FROM language WHERE id = :id), '
        '(SELECT pk FROM identifier WHERE type = :type AND lang = :lang '
        'AND description = :description AND name = :name) '
        'WHERE NOT EXISTS (SELECT 1 FROM languageidentifier '
        'WHERE language_pk = (SELECT pk FROM language WHERE id = :id) '
        'AND identifier_pk = (SELECT pk FROM identifier '
        'WHERE type = :type AND lang = :lang AND description = :description '
        'AND name = :name))').bindparams(type='name', lang='en', description='Glottolog')

    for id, name in [('naxi1246', 'Naxi'), ('ndyu1242', 'Ndyuka')]:
        op.execute(insert_ident.bindparams(name=name))
        op.execute(insert_lang_ident.bindparams(id=id, name=name))


def downgrade():
    pass
