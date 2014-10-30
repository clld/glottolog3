# coding=utf-8
"""fix identifier prefix

Revision ID: 316e1bd8f046
Revises: 282de63560e2
Create Date: 2014-10-30 10:53:22.610000

"""

# revision identifiers, used by Alembic.

revision = '316e1bd8f046'
down_revision = '282de63560e2'

import datetime

from alembic import op
import sqlalchemy as sa

MATCH_EXTRACT = [
    (': %', ':\s+(.*)'),
    ('L:%', 'L:(.*)'),
]


def upgrade():
    conn = op.get_bind()

    strip_prefix = sa.text('UPDATE identifier AS i SET updated = now(), '
        'name = substring(name from :extract) '
        'WHERE type = :type AND name LIKE :match '
        'AND NOT EXISTS (SELECT 1 FROM identifier '
            'WHERE active AND type = i.type '
            'AND description = i.description AND lang = i.lang '
            'AND name = substring(i.name from :extract))', conn)

    del_prefixed = sa.text('DELETE FROM identifier AS i '
        'WHERE type = :type AND name LIKE :match '
        'AND EXISTS (SELECT 1 FROM identifier '
            'WHERE type = i.type '
            'AND description = i.description AND lang = i.lang '
            'AND name = substring(i.name from :extract))', conn)

    del_prefixed_langident = sa.text('DELETE FROM languageidentifier AS li '
        'WHERE EXISTS (SELECT 1 FROM identifier AS i '
            'WHERE type = :type AND name LIKE :match '
            'AND pk = li.identifier_pk  '
            'AND EXISTS (SELECT 1 FROM identifier '
                'WHERE type = i.type '
                'AND description = i.description AND lang = i.lang '
                'AND name = substring(i.name from :extract)))', conn)
    
    for match, extract in MATCH_EXTRACT:
        for query in (strip_prefix, del_prefixed_langident, del_prefixed):
            query.execute(type='name', match=match, extract=extract)


def downgrade():
    pass
