# coding=utf-8
"""update hids

Revision ID: 47ce593cafd3
Revises: 50b6c9f89a8b
Create Date: 2015-07-15 12:52:07.158980

"""

# revision identifiers, used by Alembic.
revision = '47ce593cafd3'
down_revision = '50b6c9f89a8b'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute(sa.text('UPDATE language AS l SET name = :name '
        'WHERE id = :id AND EXISTS (SELECT 1 FROM languoid '
        'WHERE pk = l.pk AND hid = :before)'
        ).bindparams(id='eviy1235', before='NOCODE_Eviya', name='Viya'))
    op.execute(sa.text('UPDATE identifier SET name = :new '
        'WHERE type = :type AND description = :description AND name = :old'
        ).bindparams(new='Viya', old='Eviya', type='name', description='Glottolog'))

    op.execute(sa.text('DELETE FROM languageidentifier '
        'WHERE language_pk = (SELECT pk FROM language WHERE id = :id) '
        'AND identifier_pk = (SELECT pk FROM identifier '
        'WHERE type = :type AND name = :name)'
        ).bindparams(id='jeju1234', name='jjm', type='iso639-3'))
    op.execute(sa.text('DELETE FROM identifier '
        'WHERE type = :type AND name = :name'
        ).bindparams(name='jjm', type='iso639-3'))

    for id, before, after in [
        # Ndambomo |
        ('ndam1254', 'NOCODE_Ndambomo', 'nxo'),
        # Osamayi |
        ('osam1235', 'NOCODE_Osamayi', 'syx'),
        # Eviya -> rename to Viya!
        ('eviy1235', 'NOCODE_Eviya', 'gev'),
        # Cuba |
        ('cuba1236', 'NOCODE_Cuba', 'cbq'),
        # Palen |
        ('pale1262', 'NOCODE_Palen', 'pnl'),
        # Mur Pano |
        ('murp1234', 'NOCODE_Mur-Pano', 'tkv'),
        # Jejueo -> remove old iso code!
        ('jeju1234', 'jjm', 'jje'),
        # Tarjumo |
        ('tarj1235', 'NOCODE_Tarjumo', 'txj'),
        # Vaal-Orange |
        ('vaal1235', 'NOCODE_Vaal-Orange', 'gku'),
        # Yolngu Sign Language |
        ('yoln1234', 'NOCODE_Yolngu-Sign', 'ygs'),
        # Inuit Sign Language |
        ('inui1247', 'NOCODE_Inuit-Sign', 'iks'),
    ]:
        iso = after
        op.execute(sa.text('UPDATE language AS l SET updated = now() '
            'WHERE id = :id AND EXISTS (SELECT 1 FROM languoid '
            'WHERE pk = l.pk AND hid = :before)'
        ).bindparams(id=id, before=before))
        op.execute(sa.text('UPDATE languoid AS ll SET hid = :after '
            'WHERE hid = :before AND EXISTS (SELECT 1 FROM language '
            'WHERE pk = ll.pk AND id = :id)'
        ).bindparams(id=id, before=before, after=after))

        op.execute(sa.text('INSERT INTO identifier (created, updated, active, version, '
            'type, lang, name) '
            'SELECT now(), now(), true, 1, :type, :lang, :name '
            'WHERE NOT EXISTS (SELECT 1 FROM identifier '
            'WHERE type = :type AND lang = :lang AND name = :name)'
        ).bindparams(name=iso, type='iso639-3', lang='en'))
        op.execute(sa.text('INSERT INTO languageidentifier (created, updated, active, version, '
            'language_pk, identifier_pk) '
            'SELECT now(), now(), true, 1, '
            '(SELECT pk FROM language WHERE id = :id), '
            '(SELECT pk FROM identifier WHERE type = :type AND lang = :lang AND name = :name) '
            'WHERE NOT EXISTS (SELECT 1 FROM languageidentifier '
            'WHERE language_pk = (SELECT pk FROM language WHERE id = :id) '
            'AND identifier_pk = (SELECT pk FROM identifier '
            'WHERE type = :type AND lang = :lang AND name = :name))'
        ).bindparams(id=id, name=iso, type='iso639-3', lang='en'))


def downgrade():
    pass
