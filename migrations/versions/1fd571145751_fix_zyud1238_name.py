# coding=utf-8
"""fix zyud1238 name

Revision ID: 1fd571145751
Revises: 4c43b1dc96e1
Create Date: 2015-05-07 10:49:05.770000

"""

# revision identifiers, used by Alembic.
revision = '1fd571145751'
down_revision = '4c43b1dc96e1'

import datetime

from alembic import op
import sqlalchemy as sa

ID, BEFORE, AFTER = 'zyud1238', 'Zyudin', 'Zyuzdin'


def upgrade():
    conn = op.get_bind()

    update_name = sa.text('UPDATE language SET updated = now(), '
        'name = :after WHERE id = :id AND name = :before', conn)

    params = {'type': 'name', 'description': 'Glottolog'}

    update_ident = sa.text('UPDATE identifier SET updated = now(), '
        'name = :after WHERE type = :type AND description = :description '
        'AND name = :before', conn).bindparams(**params)

    update_name.execute(id=ID, before=BEFORE, after=AFTER)
    update_ident.execute(before=BEFORE, after=AFTER)


def downgrade():
    pass
