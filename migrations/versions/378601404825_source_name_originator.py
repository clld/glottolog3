# coding=utf-8
"""source name originator

Revision ID: 378601404825
Revises: 41a6e9acbc0d
Create Date: 2014-12-01 10:49:57.968000

"""

# revision identifiers, used by Alembic.
revision = '378601404825'
down_revision = '41a6e9acbc0d'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("""
UPDATE source
    SET name = concat_ws(' ',
        coalesce(nullif(author, ''), nullif(editor, ''), 'Anonymous'),
        coalesce(nullif(year, ''), 'n.d.'))
    WHERE name != concat_ws(' ',
        coalesce(nullif(author, ''), nullif(editor, ''), 'Anonymous'),
        coalesce(nullif(year, ''), 'n.d.'))""")


def downgrade():
    pass
