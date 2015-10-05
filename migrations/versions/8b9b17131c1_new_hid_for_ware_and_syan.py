# coding=utf-8
"""new hid for Ware and Syan

2015-10-05 13:58:18,037 WARNI new code NOCODE_Syan for existing name Syan

    Syan was promoted to language status, thus, hid and level must be changed.

2015-10-05 13:58:18,130 WARNI new code wre for existing name Ware

    Ware is an unattested language with a retired iso code


Revision ID: 8b9b17131c1
Revises: 2bfadbf902eb
Create Date: 2015-10-05 14:07:23.915874

"""

# revision identifiers, used by Alembic.
revision = '8b9b17131c1'
down_revision = '2bfadbf902eb'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute(sa.text('UPDATE language AS l SET updated = now() WHERE id = :id')\
               .bindparams(id='syan1242'))
    op.execute(sa.text(
        'UPDATE languoid AS ll SET hid = :hid, level = :level '
        'WHERE EXISTS (SELECT 1 FROM language '
        'WHERE pk = ll.pk AND id = :id)'
    ).bindparams(id='syan1242', hid='NOCODE_Syan', level='dialect'))

    op.execute(sa.text('UPDATE language AS l SET updated = now() WHERE id = :id') \
               .bindparams(id='ware1252'))
    op.execute(sa.text('UPDATE languoid AS ll SET hid = :hid '
                       'WHERE EXISTS (SELECT 1 FROM language '
                       'WHERE pk = ll.pk AND id = :id)'
                       ).bindparams(id='ware1252', hid='wre'))


def downgrade():
    pass
