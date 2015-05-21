# coding=utf-8
"""rename sera1259

Revision ID: 50b6c9f89a8b
Revises: 1fd571145751
Create Date: 2015-05-21 17:16:25.289000

"""

# revision identifiers, used by Alembic.
revision = '50b6c9f89a8b'
down_revision = '1fd571145751'

import datetime

from alembic import op
import sqlalchemy as sa

ID, BEFORE, AFTER = 'sera1259', 'Seraiki', 'Saraiki'


def upgrade():
    update_name = sa.text('UPDATE language SET updated = now(), '
        'name = :after WHERE id = :id AND name = :before')

    params = {'type': 'name', 'description': 'Glottolog', 'lang': 'en'}

    insert_ident = sa.text('INSERT INTO identifier '
        '(created, updated, active, version, type, description, lang, name) '
        'SELECT now(), now(), true, 1, :type, :description, :lang, :name '
        'WHERE NOT EXISTS (SELECT 1 FROM identifier WHERE type = :type '
        'AND description = :description AND lang = :lang AND name = :name)'
        ).bindparams(**params)

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
        ).bindparams(**params)

    op.execute(update_name.bindparams(id=ID, before=BEFORE, after=AFTER))
    op.execute(insert_ident.bindparams(name=AFTER))
    op.execute(insert_lang_ident.bindparams(id=ID, name=AFTER))


def downgrade():
    pass
