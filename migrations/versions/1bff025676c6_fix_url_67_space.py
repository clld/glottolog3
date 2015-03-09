# coding=utf-8
"""fix url 67 space

Revision ID: 1bff025676c6
Revises: d57b40e2209
Create Date: 2015-03-09 18:38:16.334000

"""

# revision identifiers, used by Alembic.
revision = '1bff025676c6'
down_revision = 'd57b40e2209'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    print(op.get_bind().execute(sa.text('UPDATE source '
        'SET url = regexp_replace(url, :pattern, :repl) '
        'WHERE url ~ :pattern '
        ).bindparams(pattern=r'^(\S{66}) (\S*)$', repl=r'\1\2')).rowcount)


def downgrade():
    pass
