# coding=utf-8
"""same name languages

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

ID_BEFORE_AFTER = [
    ('dama1262', 'Dama', 'Dama (Sierra Leone)'),
    ('gana1268', 'Ganai', 'Birrdhawal'),
    ('mang1429', 'Mango', 'Mango (China)'),
    ('ngal1301', 'Ngala', 'Ngala of Lake Chad'),
    ('tait1247', 'Taita', 'Cushitic Taita'),
    ('vili1239', 'Vili', 'Vili of Ngounie'),
    ('yaoa1239', 'Yao', 'Yebarana'),
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

    for id, before, after in ID_BEFORE_AFTER:
        op.execute(update_name.bindparams(id=id, before=before, after=after))
        op.execute(insert_ident.bindparams(name=after))
        op.execute(insert_lang_ident.bindparams(id=id, name=after))

    raise NotImplementedError


def downgrade():
    pass
