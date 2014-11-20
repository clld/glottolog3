# coding=utf-8
"""fix xpg xpq

Revision ID: 13166063c61c
Revises: 79a987d8b7
Create Date: 2014-11-20 11:23:01.621000

"""

# revision identifiers, used by Alembic.

revision = '13166063c61c'
down_revision = '79a987d8b7'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute(sa.text('UPDATE identifier AS i SET updated = now(), '
        'name = :after WHERE name = :before AND type = :type '
            'AND EXISTS (SELECT 1 FROM language AS l '
            'JOIN languageidentifier AS li ON li.language_pk = l.pk '
            'WHERE l.id = :id AND li.identifier_pk = i.pk)'
        ).bindparams(id='pequ1242', type='iso639-3', before='xpg', after='xpq'))


def downgrade():
    pass
