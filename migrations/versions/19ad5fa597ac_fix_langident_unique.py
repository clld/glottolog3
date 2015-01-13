# coding=utf-8
"""fix langident unique

Revision ID: 19ad5fa597ac
Revises: f4b1d23d113
Create Date: 2015-01-13 16:00:10.937000

"""

# revision identifiers, used by Alembic.
revision = '19ad5fa597ac'
down_revision = 'f4b1d23d113'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute(sa.text('DELETE FROM languageidentifier '
        'WHERE pk IN (SELECT pk FROM (SELECT pk, row_number() OVER '
            '(PARTITION BY language_pk, identifier_pk ORDER BY pk) AS rnum '
            'FROM languageidentifier) AS p WHERE p.rnum > 1)'))


def downgrade():
    pass
