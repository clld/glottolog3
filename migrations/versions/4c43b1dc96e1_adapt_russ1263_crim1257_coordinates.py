# coding=utf-8
"""adapt russ1263 crim1257 coordinates

Revision ID: 4c43b1dc96e1
Revises: 251f19b22119
Create Date: 2015-05-06 09:31:04.248000

"""

# revision identifiers, used by Alembic.
revision = '4c43b1dc96e1'
down_revision = '251f19b22119'

import datetime

from alembic import op
import sqlalchemy as sa

ID_BEFORE_AFTER = [
    ('russ1263', ('53.9195', '72.3926'), ('59', '50')),
    ('crim1257', ('43.8398', '28.1418'), ('45', '34.08')),
]


def upgrade():
    update_coord = sa.text('UPDATE language SET updated = now(), '
        'latitude = :lat_after, longitude = :lon_after '
        'WHERE id = :id AND latitude = :lat_before AND longitude = :lon_before')

    for id, (lat_before, lon_before), (lat_after, lon_after) in ID_BEFORE_AFTER:
        op.execute(update_coord.bindparams(id=id,
            lat_before=lat_before, lon_before=lon_before,
            lat_after=lat_after, lon_after=lon_after))


def downgrade():
    pass
