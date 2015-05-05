# coding=utf-8
"""adapt corrdinates

Revision ID: 
Revises: 
Create Date: 

"""

# revision identifiers, used by Alembic.
revision = ''
down_revision = ''

import datetime

from alembic import op
import sqlalchemy as sa

ID_BEFORE_AFTER = [
    ('russ1263', ('53.9195', '72.3926')),
    ('crim1257', ('43.8398', '28.1418')),
]


def upgrade():
    update_coord = sa.text('UPDATE language SET updated = now(), '
        'latitude = :lat_after, longitude = :lon_after '
        'WHERE id = :id AND latitude = :lat_before AND longitude = :long_before')

    for id, (lat_before, lon_before), (lat_after, lon_after) in ID_BEFORE_AFTER:
        op.execute(update_coord.bindparams(id=id,
            lat_before=lat_before, lon_before=lon_before,
            lat_after=lat_after, lon_after=lon_after))


def downgrade():
    pass
