# coding=utf-8
"""isolate inactive dialects

Revision ID: 36052643279d
Revises: 173a3e41830c
Create Date: 2014-12-18 11:51:18.156000

"""

# revision identifiers, used by Alembic.
revision = '36052643279d'
down_revision = '173a3e41830c'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute(sa.text("UPDATE languoid AS l SET father_pk = NULL, family_pk = NULL, "
        "child_family_count = (SELECT count(*) "
        "FROM treeclosuretable AS t JOIN languoid AS c ON t.child_pk = c.pk "
        "WHERE parent_pk = l.pk AND t.depth > 0 AND c.level = 'family'), "
        "child_language_count = (SELECT count(*) "
        "FROM treeclosuretable AS t JOIN languoid AS c ON t.child_pk = c.pk "
        "WHERE parent_pk = l.pk AND t.depth > 0 AND c.level = 'language'), "
        "child_dialect_count = (SELECT count(*) "
        "FROM treeclosuretable AS t JOIN languoid AS c ON t.child_pk = c.pk "
        "WHERE parent_pk = l.pk AND t.depth > 0 AND c.level = 'dialect') "
        "WHERE l.level = 'dialect' AND EXISTS (SELECT 1 FROM language "
        "WHERE pk = l.pk AND NOT active)"))


def downgrade():
    pass
