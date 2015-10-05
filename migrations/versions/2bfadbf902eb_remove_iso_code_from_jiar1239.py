# coding=utf-8
"""remove iso-code from jiar1239

Revision ID: 2bfadbf902eb
Revises: 325a611fee1c
Create Date: 2015-08-31 20:12:52.770554

"""

# revision identifiers, used by Alembic.
revision = '2bfadbf902eb'
down_revision = '325a611fee1c'

import datetime

from alembic import op
import sqlalchemy as sa

from clld.db.migration import Connection
from clld.db.models.common import Language, LanguageIdentifier, Identifier


def upgrade():
    conn = Connection(op.get_bind())
    lpk = conn.pk(Language, 'jiar1239')
    for lid in list(conn.select(LanguageIdentifier, language_pk=lpk)):
        id_ = list(conn.select(Identifier, pk=lid.identifier_pk))[0]
        if id_.type == 'iso639-3':
            conn.delete(LanguageIdentifier, pk=lid.pk)
            conn.delete(Identifier, pk=id_.pk)


def downgrade():
    pass
