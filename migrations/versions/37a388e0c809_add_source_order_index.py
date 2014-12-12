# coding=utf-8
"""add source order index

Revision ID: 37a388e0c809
Revises: 1584fd711d7d
Create Date: 2014-12-12 11:36:48.179000

"""

# revision identifiers, used by Alembic.
revision = '37a388e0c809'
down_revision = '1584fd711d7d'

import datetime

from alembic import op
import sqlalchemy as sa

NAME = 'source_updated_desc_pk_desc_key'
TABLE = 'source'
COLS = [sa.text('updated DESC'), sa.text('pk DESC')]
UNIQUE = True


def upgrade():
    conn = op.get_bind()

    has_index = sa.text('SELECT EXISTS (SELECT 1 FROM pg_indexes '
        'WHERE indexname = :name)', conn)

    if not has_index.scalar(name=NAME):
        op.create_index(NAME, TABLE, COLS, unique=UNIQUE)


def downgrade():
    pass
