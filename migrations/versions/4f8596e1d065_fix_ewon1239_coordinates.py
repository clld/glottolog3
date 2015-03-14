# coding=utf-8
"""fix ewon1239 coordinates

Revision ID: 4f8596e1d065
Revises: 1bff025676c6
Create Date: 2015-03-14 08:52:57.035000

"""

# revision identifiers, used by Alembic.
revision = '4f8596e1d065'
down_revision = '1bff025676c6'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute(sa.text('UPDATE language SET updated = now(), '
        'latitude = :longitude, longitude = :latitude '
        'WHERE id = :id AND latitude = :latitude AND longitude = :longitude'
        ).bindparams(id='ewon1239', latitude='11.9365', longitude='4.21141'))


def downgrade():
    pass
