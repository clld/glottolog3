# coding=utf-8
"""fix alt names

Revision ID: 1a3ec594cdf3
Revises: 95efeef62d
Create Date: 2013-12-19 09:08:29.907928

"""

# revision identifiers, used by Alembic.
revision = '1a3ec594cdf3'
down_revision = '95efeef62d'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    c = op.get_bind()

    # remove empty names:
    empty_names = [r[0] for r in c.execute("select pk from identifier where name = ''")]
    for pk in empty_names:
        c.execute("delete from languageidentifier where identifier_pk = %s", (pk,))
        c.execute("delete from identifier where pk = %s", (pk,))

    # remove leading and trailing whitespace from identifiers:
    update = {}
    for row in c.execute("select pk, name from identifier"):
        if row[1] and row[1] != row[1].strip():
            update[row[0]] = row[1].strip()
    for pk, name in update.items():
        c.execute("update identifier set name = %s where pk = %s", (name, pk))


def downgrade():
    pass
