# coding=utf-8
"""fix langcountry null

Revision ID: 98f845a5742
Revises: 19ad5fa597ac
Create Date: 2015-01-13 18:16:33.458000

"""

# revision identifiers, used by Alembic.
revision = '98f845a5742'
down_revision = '19ad5fa597ac'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute(sa.text('DELETE FROM languoidcountry '
        'WHERE country_pk IS NULL'))


def downgrade():
    pass
