# coding=utf-8
"""align jiar1239 status

Revision ID: 184c40fb1702
Revises: 2f35007cbe17
Create Date: 2015-04-24 12:50:28.402000

"""

# revision identifiers, used by Alembic.
revision = '184c40fb1702'
down_revision = '2f35007cbe17'

import datetime

from alembic import op
import sqlalchemy as sa

ID, ACTIVE, BEFORE, AFTER = 'jiar1239', False, 'spurious retired', 'established'


def upgrade():
    op.execute(sa.text('UPDATE languoid AS ll SET status = :after '
        'WHERE EXISTS (SELECT 1 FROM language '
        'WHERE pk = ll.pk AND id = :id AND active = :active) '
        'AND status = :before'
        ).bindparams(id=ID, active=ACTIVE, before=BEFORE, after=AFTER))
    

def downgrade():
    pass
