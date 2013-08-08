# coding=utf-8
"""make superseded languoids inactive

Revision ID: 5113368c7dbe
Revises: 2920c7a8063a
Create Date: 2013-08-08 21:41:30.992650

"""

# revision identifiers, used by Alembic.
revision = '5113368c7dbe'
down_revision = '2920c7a8063a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()
    conn.execute("update language set active = false where active = true and pk in (select languoid_pk from superseded)")


def downgrade():
    pass
