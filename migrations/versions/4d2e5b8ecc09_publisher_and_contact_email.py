# coding=utf-8
"""publisher and contact email

Revision ID: 4d2e5b8ecc09
Revises: 8b9b17131c1
Create Date: 2015-10-07 09:40:02.781895

"""

# revision identifiers, used by Alembic.
revision = '4d2e5b8ecc09'
down_revision = '8b9b17131c1'

import datetime

from alembic import op
import sqlalchemy as sa


DATA = dict(
    publisher_name='Max Planck Institute for the Science of Human History',
    publisher_place='Jena',
    publisher_url='http://www.shh.mpg.de',
    contact='glottolog@shh.mpg.de')


def upgrade():
    op.execute(sa.text("""\
UPDATE dataset SET updated = now(), %s"""
                       % ', '.join('{0} = :{0}'.format(key) for key in DATA)
                       ).bindparams(**DATA))


def downgrade():
    pass
