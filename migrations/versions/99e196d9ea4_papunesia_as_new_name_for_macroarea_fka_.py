# coding=utf-8
"""papunesia as new name for macroarea fka pacific

Revision ID: 99e196d9ea4
Revises: 1a3ec594cdf3
Create Date: 2014-01-14 09:50:57.906699

"""

# revision identifiers, used by Alembic.
revision = '99e196d9ea4'
down_revision = '1a3ec594cdf3'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()
    conn.execute('update macroarea set name = %s where id = %s', ('Papunesia', 'pacific'))

def downgrade():
    conn = op.get_bind()
    conn.execute('update macroarea set name = %s where id = %s', ('Pacific', 'pacific'))
