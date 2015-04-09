# coding=utf-8
"""fix bont1244 with bont1247

Revision ID: 27047e2c63d2
Revises: e6397d2c4ac
Create Date: 2015-04-09 15:27:08.928000

"""

# revision identifiers, used by Alembic.
revision = '27047e2c63d2'
down_revision = 'e6397d2c4ac'

import datetime

from alembic import op
import sqlalchemy as sa

ID, REPLACEMENT = 'cent2083', 'cent2292'
ISO, AFTER = 'bnc', 'bont1247'
MOVE = ['bayy1237', 'guin1256', 'sada1241']


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

    lang_deactivate.execute(id=ID)
    uoid_deactivate.execute(id=ID)
    supersede.execute(id=ID, replacement=REPLACEMENT)

    move_iso = sa.text('UPDATE languageidentifier SET updated = now(), '
        'language_pk = (SELECT pk FROM language WHERE id = :after) '
        'WHERE identifier_pk = (SELECT pk FROM identifier WHERE type = :type AND name = :iso) '
        'AND language_pk = (SELECT pk FROM language WHERE id = :before) '
        'AND EXISTS (SELECT 1 FROM language WHERE id = :before) '
        'AND EXISTS (SELECT 1 FROM language WHERE id = :after) '
        'AND EXISTS (SELECT 1 FROM identifier WHERE type = :type AND name = :iso)',
        conn).bindparams(type='iso639-3')

    move_iso.execute(iso=ISO, before=ID, after=AFTER)
    
    move_lang = sa.text('UPDATE language AS l SET updated = now() '
        'WHERE id = :id AND EXISTS (SELECT 1 FROM languoid WHERE pk = l.pk '
        'AND father_pk = (SELECT pk FROM language WHERE id = :before))', conn)
    move_uoid = sa.text('UPDATE languoid AS ll '
        'SET father_pk = (SELECT pk FROM language WHERE id = :after) '
        'WHERE EXISTS (SELECT 1 FROM language WHERE pk = ll.pk AND id = :id) '
        'AND father_pk = (SELECT pk FROM language WHERE id = :before)', conn)

    for id in MOVE:
        move_lang.execute(id=id, before=ID)
        move_uoid.execute(id=id, before=ID, after=REPLACEMENT)

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
      l.child_family_count != u.child_family_count OR
      l.child_language_count != u.child_language_count OR
      l.child_dialect_count != u.child_dialect_count)""",
]
