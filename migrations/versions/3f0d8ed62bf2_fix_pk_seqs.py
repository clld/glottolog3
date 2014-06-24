# coding=utf-8
"""fix pk seqs

Revision ID: 3f0d8ed62bf2
Revises: 162135985837
Create Date: 2014-06-24 16:29:19.469848

"""

# revision identifiers, used by Alembic.
revision = '3f0d8ed62bf2'
down_revision = '162135985837'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    affix = '_pk_seq'
    conn = op.get_bind()
    for row in conn.execute("SELECT c.relname FROM pg_class c WHERE c.relkind = 'S'").fetchall():
        seq = row[0]
        if seq.endswith(affix):
            table = seq[:-len(affix)]
        conn.execute("SELECT setval('%s', coalesce((SELECT max(pk)+1 from %s), 1), false)" % (seq, table))


def downgrade():
    pass
