# coding=utf-8
"""fix polymorhic_type

Revision ID: 41a6e9acbc0d
Revises: 13166063c61c
Create Date: 2014-11-26 11:26:50.560000

"""

# revision identifiers, used by Alembic.
revision = '41a6e9acbc0d'
down_revision = '13166063c61c'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    update_pmtype(['language', 'source'], 'base', 'custom')


def downgrade():
    update_pmtype(['language', 'source'], 'custom', 'base')


def update_pmtype(tablenames, before, after):
    for table in tablenames:
        op.execute(sa.text('UPDATE %s SET polymorphic_type = :after '
            'WHERE polymorphic_type = :before' % table
            ).bindparams(before=before, after=after))
