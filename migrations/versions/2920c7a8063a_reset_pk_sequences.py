# coding=utf-8
"""reset pk sequences

Revision ID: 2920c7a8063a
Revises: None
Create Date: 2013-08-02 09:49:40.472548

"""

# revision identifiers, used by Alembic.
revision = '2920c7a8063a'
down_revision = None

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

