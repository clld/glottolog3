# coding=utf-8
"""drop languoid classificationcomments

Revision ID: d6e1ef109e3
Revises: 26be1a82817
Create Date: 2015-04-01 14:27:59.386000

"""

# revision identifiers, used by Alembic.
revision = 'd6e1ef109e3'
down_revision = '26be1a82817'

import datetime

from alembic import op
import sqlalchemy as sa

DROP = [
    ('languoid', 'classificationcomment'),
    ('languoid', 'globalclassificationcomment'),
    ('languoid_history', 'classificationcomment'),
    ('languoid_history', 'globalclassificationcomment'),
]


def upgrade():
    conn = op.get_bind()

    has_column = sa.text('SELECT EXISTS (SELECT 1 FROM pg_attribute '
        'WHERE attrelid = (SELECT oid FROM pg_class WHERE relname = :tab) '
        'AND attname = :col)', conn)

    for tab, col in DROP:
        if has_column.scalar(tab=tab, col=col):
            op.drop_column(tab, col)


def downgrade():
    pass
