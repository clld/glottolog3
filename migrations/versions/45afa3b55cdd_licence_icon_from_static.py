# coding=utf-8
"""licence icon from static

Revision ID: 45afa3b55cdd
Revises: 3dc07b38e477
Create Date: 2015-04-07 17:05:22.854000

"""

# revision identifiers, used by Alembic.
revision = '45afa3b55cdd'
down_revision = '3dc07b38e477'

import datetime
import json

from alembic import op
import sqlalchemy as sa

BEFORE = 'http://i.creativecommons.org/l/by-sa/3.0/88x31.png'
AFTER = 'cc-by-sa.png'


def upgrade():
    conn = op.get_bind()
    select_jd = sa.text('SELECT jsondata FROM dataset WHERE id = :id', conn)
    update_jd = sa.text('UPDATE dataset SET updated = now(), '
        'jsondata = :jsondata WHERE id = :id', conn)

    jd = json.loads(select_jd.scalar(id='glottolog') or '{}')
    icon = jd.get('license_icon')
    if icon == BEFORE:
        jd['license_icon'] = AFTER
        update_jd.execute(id='glottolog', jsondata=json.dumps(jd))
        

def downgrade():
    pass
