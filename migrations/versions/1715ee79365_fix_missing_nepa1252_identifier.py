# coding=utf-8
"""fix missing nepa1252 identifier

Revision ID: 1715ee79365
Revises: 506dcac7d75
Create Date: 2015-04-15 19:34:27.655000

"""

# revision identifiers, used by Alembic.
revision = '1715ee79365'
down_revision = '506dcac7d75'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    id, name = 'nepa1252', 'Nepali'

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

    op.execute(insert_ident.bindparams(name=name))
    op.execute(insert_lang_ident.bindparams(id=id, name=name))


def downgrade():
    pass
