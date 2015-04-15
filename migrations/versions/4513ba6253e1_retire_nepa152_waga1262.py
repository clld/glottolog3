# coding=utf-8
"""retire nepa152 waga1262

Revision ID: 4513ba6253e1
Revises: 5a0f695bcecc
Create Date: 2015-04-15 18:41:42.999000

"""

# revision identifiers, used by Alembic.
revision = '4513ba6253e1'
down_revision = '5a0f695bcecc'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()

    move_lang = sa.text('UPDATE language AS l SET updated = now() '
        'WHERE id = :id AND EXISTS (SELECT 1 FROM languoid WHERE pk = l.pk '
        'AND father_pk = (SELECT pk FROM language WHERE id = :before))', conn)
    move_uoid = sa.text('UPDATE languoid AS ll '
        'SET father_pk = (SELECT pk FROM language WHERE id = :after) '
        'WHERE EXISTS (SELECT 1 FROM language WHERE pk = ll.pk AND id = :id) '
        'AND father_pk = (SELECT pk FROM language WHERE id = :before)', conn)

    update_status = sa.text('UPDATE languoid AS ll SET status = :after '
        'WHERE EXISTS (SELECT 1 FROM language WHERE pk = ll.pk AND id = :id) '
        'AND status = :before', conn)

    clear_hid = sa.text('UPDATE languoid AS ll SET hid = NULL '
        'WHERE EXISTS (SELECT 1 FROM language WHERE pk = ll.pk AND id = :id) '
        'AND hid = :before', conn)

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

    move_codes = sa.text('UPDATE languageidentifier AS li SET updated = now(), '
        'language_pk = (SELECT pk FROM language WHERE id = :after) '
        'WHERE EXISTS (SELECT 1 FROM identifier WHERE pk = li.identifier_pk '
        'AND type != :type AND name = :code) '
        'AND language_pk = (SELECT pk FROM language WHERE id = :before) ',
        conn).bindparams(type='name')
    move_names = sa.text('UPDATE languageidentifier AS li SET updated = now(), '
        'language_pk = (SELECT pk FROM language WHERE id = :after) '
        'WHERE EXISTS (SELECT 1 FROM identifier WHERE pk = li.identifier_pk AND type = :type) '
        'AND language_pk = (SELECT pk FROM language WHERE id = :before)',
        conn).bindparams(type='name')

    move_author_refs = sa.text('UPDATE languagesource AS ls SET updated = now(), '
        'language_pk = (SELECT pk FROM language WHERE id = :after) '
        'WHERE EXISTS (SELECT 1 FROM source WHERE pk = ls.source_pk AND author = :author) '
        'AND language_pk = (SELECT pk FROM language WHERE id = :before)', conn)

    id, before, after = 'waga1262', 'suau1243', 'book1242'
    child_dialects = ['gama1252', 'nucl1501']
    move_lang.execute(id=id, before=before)
    move_uoid.execute(id=id, before=before, after=after)
    for dialect_id in child_dialects:
        move_lang.execute(id=dialect_id, before=id)
        move_uoid.execute(id=dialect_id, before=id, after='waga1268')
    update_status.execute(id=id, before='established', after='spurious retired')
    clear_hid.execute(id=id, before='wgw')

    id, replacement, iso_replacement = 'nepa1252', 'nepa1254', 'east1436'
    child_dialects = ['acch1238', 'bait1246', 'bajh1238', 'baju1244', 'darj1238',
                      'dote1238', 'gork1241', 'nucl1265', 'palp1241', 'sora1251']
    lang_deactivate.execute(id=id)
    uoid_deactivate.execute(id=id)
    clear_hid.execute(id=id, before='nep')
    supersede.execute(id=id, replacement=replacement)
    for dialect_id in child_dialects:
        move_lang.execute(id=dialect_id, before=id)
        move_uoid.execute(id=dialect_id, before=id, after=replacement)
    move_codes.execute(code='nep', before=id, after=iso_replacement)
    move_names.execute(before=id, after=replacement)
    move_author_refs.execute(author='ISO 639-3 Registration Authority', before=id, after=iso_replacement)

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
