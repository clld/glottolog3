# coding=utf-8
"""fix boan1244 mojibake

Revision ID: 506dcac7d75
Revises: 4513ba6253e1
Create Date: 2015-04-15 19:20:59.059000

"""

# revision identifiers, used by Alembic.
revision = '506dcac7d75'
down_revision = '4513ba6253e1'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    id, before, after = 'boan1244', u'Bo\xc3\xabng', u'Bo\xebng'

    update_name = sa.text('UPDATE language SET updated = now(), '
        'name = :after WHERE id = :id AND name = :before')
    update_ident = sa.text('UPDATE identifier SET updated = now(), '
        'name = :after WHERE type = :type AND name = :before ')

    op.execute(update_name.bindparams(id=id, before=before, after=after))
    op.execute(update_ident.bindparams(type='name', before=before, after=after))


def downgrade():
    pass
