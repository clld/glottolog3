# coding=utf-8
"""fix hua1248 and xooo1239 dialects

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

MOVE = [
    ('huaa1249', 'huaa1248', 'hoaa1235'),
    ('sasi1238', 'huaa1248', 'hoaa1235'),
    ('auni1244', 'xooo1239', 'lowe1407'),
    ('kiha1240', 'xooo1239', 'lowe1407'),
    ('xati1238', 'xooo1239', 'lowe1407'),
]

RETIRE = ['kaki1248', 'kwii1242', 'nusa1243']

MERGE = [('ngue1241', 'ngue1242')]


def upgrade():
    pass


def downgrade():
    pass
