# coding=utf-8
"""drop doctypes_str proviers_str

Revision ID: 1584fd711d7d
Revises: 53b80531e21e
Create Date: 2014-12-12 10:44:56.968000

"""

# revision identifiers, used by Alembic.
revision = '1584fd711d7d'
down_revision = '53b80531e21e'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()

    has_column = sa.text('SELECT EXISTS '
        '(SELECT 1 FROM information_schema.columns '
        'WHERE table_name = :tab and column_name = :col)', conn)

    for tab, col in [('ref', 'doctypes_str'), ('ref', 'providers_str')]:
        if has_column.scalar(tab=tab, col=col):
            op.drop_column(tab, col)


def downgrade():
    pass
