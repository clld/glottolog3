# coding=utf-8
"""drop degruyter ca doctypes

Revision ID: 1c514da366b7
Revises: d6e1ef109e3
Create Date: 2015-04-07 13:04:36.148000

"""

# revision identifiers, used by Alembic.
revision = '1c514da366b7'
down_revision = 'd6e1ef109e3'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("""DELETE FROM refdoctype AS rd
    WHERE EXISTS (SELECT 1 FROM refprovider AS rp WHERE rp.ref_pk = rd.ref_pk
        AND rp.provider_pk = (SELECT pk FROM provider WHERE id = 'degruyter'))
    AND NOT EXISTS (SELECT 1 FROM refprovider AS rp WHERE rp.ref_pk = rd.ref_pk
        AND rp.provider_pk != (SELECT pk FROM provider WHERE id = 'degruyter'))
    AND EXISTS (SELECT 1 FROM ref WHERE pk = rd.ref_pk
        AND ca_doctype_trigger IS NOT NULL)""")

def downgrade():
    pass
