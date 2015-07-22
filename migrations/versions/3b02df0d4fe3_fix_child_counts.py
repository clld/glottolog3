# coding=utf-8
"""fix child counts

Revision ID: 3b02df0d4fe3
Revises: 47ce593cafd3
Create Date: 2015-07-21 18:02:26.358000

"""

# revision identifiers, used by Alembic.
revision = '3b02df0d4fe3'
down_revision = '47ce593cafd3'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    for sql in RECREATE_TREECLOSURE:
        op.execute(sql)


def downgrade():
    pass


RECREATE_TREECLOSURE = [
    """DELETE FROM treeclosuretable""",
    """WITH RECURSIVE tree(child_pk, parent_pk, depth) AS (
      SELECT pk, pk, 0 FROM languoid
    UNION ALL
      SELECT t.child_pk, p.father_pk, t.depth + 1
      FROM languoid AS p
      JOIN tree AS t ON p.pk = t.parent_pk
      WHERE p.father_pk IS NOT NULL
    )
    INSERT INTO treeclosuretable (created, updated, active, child_pk, parent_pk, depth)
    SELECT now(), now(), true, * FROM tree""",
    """UPDATE languoid AS l SET family_pk = u.family_pk
    FROM (WITH RECURSIVE tree(child_pk, parent_pk, depth) AS (
      SELECT pk, father_pk, 1 FROM languoid
    UNION ALL
      SELECT t.child_pk, p.father_pk, t.depth + 1
      FROM languoid AS p
      JOIN tree AS t ON p.pk = t.parent_pk
      WHERE p.father_pk IS NOT NULL
    )
    SELECT DISTINCT ON (child_pk) child_pk, parent_pk AS family_pk
    FROM tree ORDER BY child_pk, depth DESC) AS u
    WHERE l.pk = u.child_pk AND l.family_pk IS DISTINCT FROM u.family_pk""",
    """UPDATE languoid AS l SET
      child_family_count = u.child_family_count,
      child_language_count = u.child_language_count,
      child_dialect_count = u.child_dialect_count
    FROM (WITH RECURSIVE tree(child_pk, parent_pk, level) AS (
      SELECT pk, father_pk, level FROM languoid
    UNION ALL
      SELECT t.child_pk, p.father_pk, t.level
      FROM languoid AS p
      JOIN tree AS t ON p.pk = t.parent_pk
      WHERE p.father_pk IS NOT NULL
    )
    SELECT pk,
      count(nullif(tree.level != 'family', true)) AS child_family_count,
      count(nullif(tree.level != 'language', true)) AS child_language_count,
      count(nullif(tree.level != 'dialect', true)) AS child_dialect_count
    FROM languoid LEFT JOIN tree ON pk = tree.parent_pk
    GROUP BY pk) AS u
    WHERE l.pk = u.pk AND (
      COALESCE(l.child_family_count, -1) != u.child_family_count OR
      COALESCE(l.child_language_count, -1) != u.child_language_count OR
      COALESCE(l.child_dialect_count, -1) != u.child_dialect_count)""",
]
