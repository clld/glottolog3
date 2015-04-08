# coding=utf-8
"""merge dialect language

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

ID_REPLACEMENT = [
    ('boka1247', 'boka1249'),
    ('mila1244', 'mila1245'),
    ('tang1337', 'tang1377'),
]


def upgrade():
    conn = op.get_bind()
    deactivate = sa.text('UPDATE languoid AS ll SET updated = now(), '
        'active = FALSE, father_pk = NULL WHERE EXISTS (SELECT 1 FROM language '
        'WHERE pk = ll.pk AND id = :id)', conn)
    unlink = [sa.text('DELETE FROM %s WHERE EXISTS '
        '(SELECT 1 FROM language WHERE pk = %s.languoid_pk AND id = :id)' % (tab, tab), conn)
        for tab in ('languoidcountry', 'languoidmacroarea')]
    for id, replacement in ID_REPLACEMENT:
        deactivate.execute(id=id)
        for u in unlink:
            u.execute(id=id)

    raise NotImplementedError


def downgrade():
    pass
