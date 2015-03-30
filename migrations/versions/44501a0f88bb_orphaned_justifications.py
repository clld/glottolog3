# coding=utf-8
"""orphaned justifications

Revision ID: 44501a0f88bb
Revises: 2d3af03ac4b3
Create Date: 2015-03-30 18:03:10.989000

"""

# revision identifiers, used by Alembic.
revision = '44501a0f88bb'
down_revision = '2d3af03ac4b3'

import datetime

from alembic import op
import sqlalchemy as sa

OLD_NEW = [  # see https://github.com/clld/glottolog-data/commit/c41fce7be601e32ab7a95724bfbcc06a87ae35a5
    ('21098', '13538'),
    ('26119', '120649'),
    ('40008', '10790'),    #
    ('62158', '54471'),
    ('94595', '92551'),    #
    ('109313', '56080'),
    ('132826', '31549'),
    ('158804', '92322'),
    ('303233', '121865'),  #
    ('304285', '82908'),
    ('304913', '130142'),  #
    ('307893', '9640'),    #
    ('311844', '15234'),   #
]


def upgrade():
    update_just = sa.text('UPDATE valuesetreference AS vsr SET updated = now(), '
        'source_pk = (SELECT pk FROM source WHERE id = :new) '
        'WHERE EXISTS (SELECT 1 FROM source WHERE pk = vsr.source_pk '
        'AND id = :old)')
    for old, new in OLD_NEW:
        op.execute(update_just.bindparams(old=old, new=new))


def downgrade():
    pass
