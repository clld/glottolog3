# coding=utf-8
"""change identifier unique

Revision ID: 
Revises: 
Create Date: 

"""

# revision identifiers, used by Alembic.

revision = ''
down_revision = ''

import datetime

from alembic import op
import sqlalchemy as sa

TABLE = 'identifier'
OLD = ['name', 'type', 'description']
NEW = ['name', 'type', 'description', 'lang']
OLD_NAME = 'identifier_name_type_description_key'
NEW_NAME = 'identifier_name_type_description_lang_key'


def replace(table, old, new_name, new):
    conn = op.get_bind()

    select_name = sa.text('SELECT c.conname FROM pg_constraint AS c '
        'JOIN pg_class AS r ON r.oid = c.conrelid '
        'WHERE r.relname = :table '
        'AND pg_get_constraintdef(c.oid) = :definition', conn)

    old_name = select_name.scalar(table=table,
        definition='UNIQUE (%s)' % ', '.join(old))

    if old_name:
        op.drop_constraint(old_name, table)

    has_new = select_name.scalar(table=table,
        definition='UNIQUE (%s)' % ', '.join(new))

    if not has_new:
        op.create_unique_constraint(new_name, table, new)


def upgrade():
    replace(TABLE, OLD, NEW_NAME, NEW)
    
    
def downgrade():
    replace(TABLE, NEW, OLD_NAME, OLD)
