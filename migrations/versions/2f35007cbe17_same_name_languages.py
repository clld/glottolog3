# coding=utf-8
"""same name languages

Revision ID: 2f35007cbe17
Revises: 5b112e7fb9
Create Date: 2015-04-24 11:30:15.361000

"""

# revision identifiers, used by Alembic.
revision = '2f35007cbe17'
down_revision = '5b112e7fb9'

import datetime

from alembic import op
import sqlalchemy as sa


ID_BEFORE_AFTER = [
    ('dama1262', 'Dama', 'Dama (Sierra Leone)'),
    ('dama1267', 'Dama', 'Dama (Cameroon)'),
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

    params = {'type': 'name', 'description': 'Glottolog', 'lang': 'en'}

    unlink_ident = sa.text('DELETE FROM languageidentifier AS li '
        'WHERE language_pk = (SELECT pk FROM language WHERE id = :id) '
        'AND EXISTS (SELECT 1 FROM identifier WHERE pk = li.identifier_pk '
            'AND type = :type AND description = :description AND lang = :lang '
            'AND name = :before)').bindparams(**params)

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

    delete_orphans = sa.text('DELETE FROM identifier AS i '
        'WHERE NOT EXISTS (SELECT 1 FROM languageidentifier '
        'WHERE identifier_pk = i.pk)')

    for id, before, after in ID_BEFORE_AFTER:
        op.execute(update_name.bindparams(id=id, before=before, after=after))
        op.execute(unlink_ident.bindparams(id=id, before=before))
        op.execute(insert_ident.bindparams(name=after))
        op.execute(insert_lang_ident.bindparams(id=id, name=after))

    op.execute(delete_orphans)


def downgrade():
    pass
