# coding=utf-8
"""new hid for Lawu

Revision ID: 325a611fee1c
Revises: 3b02df0d4fe3
Create Date: 2015-08-31 17:16:30.845851

"""

# revision identifiers, used by Alembic.
revision = '325a611fee1c'
down_revision = '3b02df0d4fe3'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    affix = '_pk_seq'
    conn = op.get_bind()
    for row in conn.execute("SELECT c.relname FROM pg_class c WHERE c.relkind = 'S'").fetchall():
        seq = row[0]
        if seq.endswith(affix):
            table = seq[:-len(affix)]
        conn.execute("SELECT setval('%s', coalesce((SELECT max(pk)+1 from %s), 1), false)" % (seq, table))

    for id, before, after in [
        # Lawu
        ('lawu1238', 'NOCODE_Lawu', 'lwu'),
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
