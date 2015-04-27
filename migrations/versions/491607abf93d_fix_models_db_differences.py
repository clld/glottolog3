# coding=utf-8
"""fix models db differences

Revision ID: 491607abf93d
Revises: 2793805922ab
Create Date: 2015-04-27 13:19:30.567000

"""

# revision identifiers, used by Alembic.
revision = '491607abf93d'
down_revision = '2793805922ab'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_table('unitparameterunit')
    op.drop_table('unitparameterunit_history')

    with op.batch_alter_table('ref_history') as b:
        b.add_column(sa.Column('language_note', sa.Unicode))
        b.add_column(sa.Column('ca_language_trigger', sa.Unicode))
        b.add_column(sa.Column('ca_doctype_trigger', sa.Unicode))


def downgrade():
    pass
