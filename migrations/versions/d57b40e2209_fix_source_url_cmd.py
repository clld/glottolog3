# coding=utf-8
"""fix source url cmd

Revision ID: d57b40e2209
Revises: 539dddb4e602
Create Date: 2015-03-09 13:12:29.791000

"""

# revision identifiers, used by Alembic.
revision = 'd57b40e2209'
down_revision = '539dddb4e602'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    print(op.get_bind().execute(sa.text('UPDATE source '
        'SET url = substring(url FROM :pattern) '
        'WHERE url ~ :pattern '
        ).bindparams(pattern=r'^\\url\{(.+)\}$')).rowcount)


def downgrade():
    pass
