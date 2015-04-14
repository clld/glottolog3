# coding=utf-8
"""bookkeeping name

Revision ID: 5a0f695bcecc
Revises: 92df9fa681e
Create Date: 2015-04-14 11:35:28.347000

"""

# revision identifiers, used by Alembic.
revision = '5a0f695bcecc'
down_revision = '92df9fa681e'

import datetime

from alembic import op
import sqlalchemy as sa

ID, BEFORE, AFTER = 'book1242', 'Book keeping', 'Bookkeeping'

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

    op.execute(update_name.bindparams(id=ID, before=BEFORE, after=AFTER))
    op.execute(insert_ident.bindparams(name=AFTER))
    op.execute(insert_lang_ident.bindparams(id=ID, name=AFTER))


def downgrade():
    pass
