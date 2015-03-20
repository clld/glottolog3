# coding=utf-8
"""fix_pks

Revision ID: 63debe586cd
Revises: 1de11a1651f7
Create Date: 2015-03-19 13:20:07.079149

"""

# revision identifiers, used by Alembic.
revision = '63debe586cd'
down_revision = 'f17360a2b38'#'1de11a1651f7'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
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
