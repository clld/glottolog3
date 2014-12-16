# coding=utf-8
"""new languages

Revision ID: 
Revises: 
Create Date: 

"""

# revision identifiers, used by Alembic.
revision = ''
down_revision = ''

import datetime
import json

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()

    def update_languoid(col):
        yield sa.text('UPDATE language AS l SET updated = now(), '
            'WHERE id = :id AND EXISTS (SELECT 1 FROM languoid '
            'WHERE pk = l.pk AND %s = :before' % col, conn)
        yield sa.text('UPDATE languoid AS ll SET %s = :after '
            'WHERE %s = :before AND EXISTS (SELECT 1 FROM language '
            'WHERE pk = ll.pk AND id = :id)', conn)

    def insert_ident(type, lang):
        yield sa.text('INSERT INTO identifier (created, updated, active, version, '
            'type, lang, name) '
            'SELECT now(), now(), true, 1, :type, :lang, :name '
            'WHERE NOT EXISTS (SELECT 1 FROM identifier '
            'WHERE type = :type AND lang = :lang AND name = :name)',
            conn).bindparams(type=type, lang=lang)
        yield sa.text('INSERT INTO languageidentifier (created, updated, active, version, '
            'language_pk, identifier_pk) '
            'SELECT now(), now(), true, 1, '
            '(SELECT pk FROM language WHERE id = :id), '
            '(SELECT pk FROM identifier WHERE type = :type AND lang = :lang AND name = :name) '
            'WHERE NOT EXISTS (SELECT 1 FROM languageidentifier '
            'WHERE language_pk = (SELECT pk FROM language WHERE id = :id) '
            'AND identifier_pk = (SELECT pk FROM identifier '
            'WHERE type = :type AND lang = :lang AND name = :name))',
            conn).bindparams(type=type, lang=lang)

    def update_json(id, after):
        before = json.loads(sa.text('SELECT jsondata FROM language '
            'WHERE id = :id', conn).scalar(id=id))
        if after != before:
            sa.text('UPDATE language SET jsondata = :after '
                'WHERE id = :id', conn).execute(id=id, after=json.dumps(after))
        
    # Damu

    # Umbrian
    for update in update_languoid('level'):
        update.execute(id='umbr1253', before='dialect', after='language')

    # Yugh

    # Paranan (nothing to do)

    # Yaygir
    for update in update_languoid('hid'):
        update.execute(id='yayg1236', before='yyg', after='xya')
    for insert in insert_ident(type='iso639-3', lang='en'):
        insert.execute(id='yayg1236', name='xya')

    # Naxi
    for update in update_languoid('hid'):
        update.execute(id='naxi1245', before='nbf', after='nxq')


def downgrade():
    pass
