# coding=utf-8
"""ca handling

Revision ID: 162135985837
Revises: 10acd02fac9a
Create Date: 2014-06-24 09:37:40.271694

"""

# revision identifiers, used by Alembic.
revision = '162135985837'
down_revision = '10acd02fac9a'

import datetime

from alembic import op
import sqlalchemy as sa


COLS = 'language_note ca_language_trigger ca_doctype_trigger'.split()


def upgrade():
    for col in COLS:
        op.add_column('ref', sa.Column(col, sa.Unicode))


def downgrade():
    for col in COLS:
        op.drop_column('ref', col)
