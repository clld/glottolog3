# coding=utf-8
"""fix valuesetref unique

Revision ID: 453449671748
Revises: 98f845a5742
Create Date: 2015-01-13 18:19:45.110000

"""

# revision identifiers, used by Alembic.
revision = '453449671748'
down_revision = '98f845a5742'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute(sa.text('DELETE FROM valuesetreference '
        'WHERE pk IN (SELECT pk FROM (SELECT pk, row_number() OVER '
            '(PARTITION BY valueset_pk, source_pk ORDER BY pk) AS rnum '
            'FROM valuesetreference) AS p WHERE p.rnum > 1)'))


def downgrade():
    pass
