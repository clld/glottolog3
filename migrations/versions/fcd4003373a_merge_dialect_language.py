# coding=utf-8
"""merge dialect language

Revision ID: fcd4003373a
Revises: 45afa3b55cdd
Create Date: 2015-04-09 13:23:46.829000

"""

# revision identifiers, used by Alembic.
revision = 'fcd4003373a'
down_revision = '45afa3b55cdd'

import datetime

from alembic import op
import sqlalchemy as sa


ID_REPLACEMENT = [
    ('boka1247', 'boka1249'),
    ('mila1244', 'mila1245'),
    ('tang1337', 'tang1377'),
]

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
      l.child_family_count != u.child_family_count OR
      l.child_language_count != u.child_language_count OR
      l.child_dialect_count != u.child_dialect_count)""",
]


def upgrade():
    conn = op.get_bind()
    lang_deactivate = sa.text('UPDATE language SET updated = now(), '
        'active = FALSE WHERE id = :id AND active ', conn)
    uoid_deactivate = sa.text('UPDATE languoid AS ll SET father_pk = NULL '
        'WHERE father_pk IS NOT NULL AND EXISTS (SELECT 1 FROM language '
        'WHERE pk = ll.pk AND id = :id )', conn)
    supersede = sa.text('INSERT INTO superseded '
        '(created, updated, active, languoid_pk, replacement_pk) '
        'SELECT now(), now(), true, '
            '(SELECT pk FROM language WHERE id = :id), '
            '(SELECT pk FROM language WHERE id = :replacement) '
        'WHERE NOT EXISTS (SELECT 1 FROM superseded '
        'WHERE languoid_pk = (SELECT pk FROM language WHERE id = :id) '
        'AND replacement_pk = (SELECT pk FROM language WHERE id = :replacement)) '
        'AND EXISTS (SELECT 1 FROM language WHERE id = :id) '
        'AND EXISTS (SELECT 1 FROM language WHERE id = :replacement)', conn)

    for id, replacement in ID_REPLACEMENT:
        lang_deactivate.execute(id=id)
        uoid_deactivate.execute(id=id)
        supersede.execute(id=id, replacement=replacement)

    for sql in RECREATE_TREECLOSURE:
        op.execute(sql)


def downgrade():
    pass
