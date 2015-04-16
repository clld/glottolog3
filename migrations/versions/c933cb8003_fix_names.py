# coding=utf-8
"""fix names

Revision ID: c933cb8003
Revises: 1715ee79365
Create Date: 2015-04-16 15:29:26.507000

"""

# revision identifiers, used by Alembic.
revision = 'c933cb8003'
down_revision = '1715ee79365'

import datetime

from alembic import op
import sqlalchemy as sa

ID_BEFORE_AFTER = [
    ('abda1238', u'`Abd Al-Kuri', u"'Abd Al-Kuri"),
    ('aden1242', u'`Aden', u"'Aden"),
    ('beda1249', u'Be:da', u'Beda'),
    ('east2520', u'East_Timor', u'East Timor'),
    ('naha1260', u'Nahari *Bhili)', u'Nahari (Bhili)'),
    ('oils1235', u'O\xefl_Southeastern', u'O\xefl Southeastern'),
    ('sana1296', u'San`a', "San'a"),
]


def upgrade():
    conn = op.get_bind()

    update_name = sa.text('UPDATE language SET updated = now(), '
        'name = :after WHERE id = :id AND name = :before', conn)

    params = {'type': 'name', 'description': 'Glottolog'}

    update_ident = sa.text('UPDATE identifier SET updated = now(), '
        'name = :after WHERE type = :type AND description = :description '
        'AND name = :before', conn).bindparams(**params)

    for id, before, after in ID_BEFORE_AFTER:
        update_name.execute(id=id, before=before, after=after)
        update_ident.execute(before=before, after=after)


def downgrade():
    pass
