# coding=utf-8
"""iso updates

Revision ID: 20b0b763f2f9
Revises: 53f4e74ce460
Create Date: 2014-10-09 12:51:21.612004

"""

# revision identifiers, used by Alembic.
revision = '20b0b763f2f9'
down_revision = '53f4e74ce460'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    """
gmo     6.57645 37.1381
stc     -10.6771        165.835
lto     0.2975  34.6961
lks     0.1529  34.5708
lsm     0.3652  34.0335
lrt     -8.4746 122.7619
aqz     -12.8322        -60.9716
    """
    pass

def downgrade():
    pass

