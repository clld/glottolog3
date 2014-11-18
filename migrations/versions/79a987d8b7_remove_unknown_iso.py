# coding=utf-8
"""remove unknown iso

Revision ID: 79a987d8b7
Revises: 56616ae95a23
Create Date: 2014-11-18 15:57:48.906000

"""

# revision identifiers, used by Alembic.

revision = '79a987d8b7'
down_revision = '56616ae95a23'

import datetime

from alembic import op
import sqlalchemy as sa

UNKNOWN = [  # 19
    ('ekb', 'ekaa1234', 'rejected'),
    ('jmk', 'jamt1238', None),
    ('lly', 'yang1304', 'rejected'),
    ('lxu', 'xuzh1234', 'rejected'),
    ('qbb', 'oldl1238', 'private'),
    ('qcs', 'tapa1260', 'private'),
    ('qer', 'dale1238', 'private'),
    ('qgg', 'ammo1234', 'private'),
    ('qgu', 'wulg1239', 'private'),
    ('qhr', 'sabe1248', 'private'),
    ('qkn', 'oldk1250', 'private'),
    ('qlm', 'limo1249', 'private'),
    ('qmx', 'oldi1244', 'private'),
    ('qok', 'oldk1249', 'private'),
    ('qpp', 'pais1238', 'private'),
    ('scy', 'scan1238', 'rejected'),
    ('svl', 'sout3210', 'rejected'),
    ('tzi', 'situ1238', 'rejected'),
    ('yyg', 'yayg1236', None)
]


def upgrade():
    params = {'type': 'iso639-3',
        'isos': [iso for iso, glottocode, kind in UNKNOWN]}
    op.execute(sa.text('DELETE FROM languageidentifier AS li '
        'WHERE EXISTS (SELECT 1 FROM identifier WHERE pk = li.identifier_pk '
            'AND type = :type AND name = ANY(:isos))'
        ).bindparams(**params))
    op.execute(sa.text('DELETE FROM identifier '
        'WHERE type = :type AND name = ANY(:isos)'
        ).bindparams(**params))


def downgrade():
    pass
