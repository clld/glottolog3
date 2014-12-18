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
        yield sa.text('UPDATE language AS l SET updated = now() '
            'WHERE id = :id AND EXISTS (SELECT 1 FROM languoid '
            'WHERE pk = l.pk AND %s = :before)' % col, conn)
        yield sa.text('UPDATE languoid AS ll SET %s = :after '
            'WHERE %s = :before AND EXISTS (SELECT 1 FROM language '
            'WHERE pk = ll.pk AND id = :id)' % (col, col), conn)

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

    update_ident = sa.text('UPDATE identifier SET updated = now(), '
        'name = :after WHERE name = :before AND type = :type', conn)

    select_json = sa.text('SELECT jsondata FROM language WHERE id = :id', conn)

    update_json = sa.text('UPDATE language SET updated = now(), '
        'jsondata = :after WHERE id = :id', conn)

    def insert_languoid(level, status, pm_type='custom'):
        yield sa.text('INSERT INTO language (created, updated, active, version, '
            'polymorphic_type, jsondata, id, name) '
            'SELECT now(), now(), true, 1, :pm_type, :jsondata, :id, :name '
            'WHERE NOT EXISTS (SELECT 1 FROM language WHERE id = :id)',
            conn).bindparams(pm_type=pm_type)
        yield sa.text('INSERT INTO languoid (pk, hid, level, status, '
            'child_family_count, child_language_count, child_dialect_count) '
            'SELECT (SELECT pk FROM language WHERE id = :id), '
            ':hid, :level, :status, 0, 0, 0 '
            'WHERE NOT EXISTS (SELECT 1 FROM languoid '
            'WHERE pk = (SELECT pk FROM language WHERE id = :id))',
            conn).bindparams(level=level, status=status)
        
    # Damu

    # Umbrian
    for update in update_languoid('level'):
        update.execute(id='umbr1253', before='dialect', after='language')
    for update in update_languoid('hid'):
        update.execute(id='umbr1253', before=None, after='xum')
    for insert in insert_ident(type='iso639-3', lang='en'):
        insert.execute(id='umbr1253', name='xum')

    # Yugh
    for update in update_languoid('hid'):
        update.execute(id='yugh1240', before=None, after='yuu')

    # Paranan (Glottolog: Subfamily Paranan-Pahanan)
    for update in update_languoid('hid'):
        update.execute(id='para1320', before=None, after='agp')

    # Yaygir
    for update in update_languoid('hid'):
        update.execute(id='yayg1236', before='yyg', after='xya')
    for insert in insert_ident(type='iso639-3', lang='en'):
        insert.execute(id='yayg1236', name='xya')

    # Naxi
    for update in update_languoid('hid'):
        update.execute(id='naxi1245', before='nbf', after='nxq')
    update_ident.execute(type='iso639-3', before='nbf', after='nxq')
    jd_before = json.loads(select_json.scalar(id='naxi1245'))
    jd_after = jd_before.copy()
    rt = jd_after.pop('iso_retirement', None)
    if jd_after != jd_before:
        update_json.execute(id='naxi1245', after=json.dumps(jd_after))
    for insert in insert_languoid('language', 'spurious retired'):
        insert.execute(id='naxi1246', name='Naxi', hid='nbf',
            jsondata=json.dumps({'iso_retirement': rt} if rt else {}))
    for insert in insert_ident(type='iso639-3', lang='en'):
        insert.execute(id='naxi1246', name='nbf')


def downgrade():
    pass
