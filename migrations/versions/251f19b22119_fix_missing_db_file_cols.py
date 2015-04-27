# coding=utf-8
"""fix missing db file cols

Revision ID: 251f19b22119
Revises: 491607abf93d
Create Date: 2015-04-27 15:27:24.097000

"""

# revision identifiers, used by Alembic.
revision = '251f19b22119'
down_revision = '491607abf93d'

import datetime

from alembic import op
import sqlalchemy as sa

TABLES = [
    'contribution_files',
    'contribution_files_history',
    'contributor_files',
    'contributor_files_history',
    'dataset_files',
    'dataset_files_history',
    'domainelement_files',
    'domainelement_files_history',
    'language_files',
    'language_files_history',
    'parameter_files',
    'parameter_files_history',
    'sentence_files',
    'sentence_files_history',
#    'source_files',  # see c80f2d77379_update_source_files_schema.py
    'source_files_history',
    'unit_files',
    'unit_files_history',
    'unitdomainelement_files',
    'unitdomainelement_files_history',
    'unitparameter_files',
    'unitparameter_files_history',
    'unitvalue_files',
    'unitvalue_files_history',
    'value_files',
    'value_files_history',
    'valueset_files',
    'valueset_files_history',
]

COLS = [
    sa.Column('id', sa.String, unique=True),
    sa.Column('description', sa.Unicode),
    sa.Column('markup_description', sa.Unicode),
    sa.Column('mime_type', sa.String),
]


def upgrade():
    for table in TABLES:
        for C in COLS:
            col = C.copy()
            if table.endswith('_files_history') and col.name == 'id':
                col.unique = False
            op.add_column(table, col)


def downgrade():
    for table in TABLES:
        for col in COLS:
            op.drop_column(table, col.name)
