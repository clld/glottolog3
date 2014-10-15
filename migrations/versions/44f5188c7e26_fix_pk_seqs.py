# coding=utf-8

"""fix pk seqs

Revision ID: 44f5188c7e26
Revises: 53f4e74ce460
Create Date: 2014-10-15 11:10:11.925000

"""

# revision identifiers, used by Alembic.
revision = '44f5188c7e26'
down_revision = '53f4e74ce460'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    # http://wiki.postgresql.org/wiki/Fixing_Sequences
    query = sa.text("""SELECT 'SELECT setval(' ||
          quote_literal(quote_ident(s.relname)) ||
          ', coalesce(max(' ||
          quote_ident(c.attname) ||
          '), 1)) FROM ' ||
          quote_ident(t.relname)
        FROM pg_class AS s
        JOIN pg_depend AS d ON d.objid = s.oid
        JOIN pg_class AS t ON t.oid = d.refobjid
        JOIN pg_attribute AS c ON c.attrelid = d.refobjid AND c.attnum = d.refobjsubid
        WHERE s.relkind = 'S'""")
    conn = op.get_bind()
    for setval, in conn.execute(query):
        conn.execute(setval)


def downgrade():
    pass
