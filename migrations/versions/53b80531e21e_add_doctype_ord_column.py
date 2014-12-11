# coding=utf-8
"""add doctype ord column

Revision ID: 53b80531e21e
Revises: 1baf716afcd9
Create Date: 2014-12-11 10:14:49.350000

"""

# revision identifiers, used by Alembic.
revision = '53b80531e21e'
down_revision = '1baf716afcd9'

import datetime

from alembic import op
import sqlalchemy as sa

DOCTYPES = [  # cf. glottolog3.models
    'grammar',
    'grammarsketch',
    'dictionary',
    'specificfeature',
    'phonology',
    'text',
    'newtestament',
    'wordlist',
    'comparative',
    'minimal',
    'socling',
    'dialectology',
    'overview',
    'ethnographic',
    'bibliographical',
    'unknown']


def upgrade():
    op.add_column('doctype', sa.Column('ord', sa.Integer))

    conn = op.get_bind()

    update_doctype = sa.text('UPDATE doctype SET updated = now(), '
        'ord = :ord WHERE id = :id AND ord IS DISTINCT FROM :ord', conn)

    id_ord = [{'id': id, 'ord': i} for i, id in enumerate(DOCTYPES, 1)]

    update_doctype.execute(id_ord)


def downgrade():
    op.drop_column('doctype', 'ord')
