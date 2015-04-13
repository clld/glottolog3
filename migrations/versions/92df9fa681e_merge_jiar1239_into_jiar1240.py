# coding=utf-8
"""merge jiar1239 into jiar1240

Revision ID: 92df9fa681e
Revises: 27047e2c63d2
Create Date: 2015-04-13 13:22:25.471000

"""

# revision identifiers, used by Alembic.
revision = '92df9fa681e'
down_revision = '27047e2c63d2'

import datetime
import json

from alembic import op
import sqlalchemy as sa


MOVE = [
    ('sida1238', 'jiar1239', 'zbua1234'),
    ('jinc1238', 'situ1239', 'situ1238'),
    ('lixi1238', 'situ1239', 'situ1238'),
    ('maer1238', 'situ1239', 'situ1238'),
    ('xiao1244', 'situ1239', 'situ1238'),
]

MERGE = [
    ('jiar1239', 'jiar1240'),
    ('chab1238', 'japh1234'),
    ('caod1238', 'tsho1240'),
    ('ribu1240', 'zbua1234'),
    ('situ1239', 'situ1238'),
]


def upgrade():
    conn = op.get_bind()
    move_lang = sa.text('UPDATE language AS l SET updated = now() '
        'WHERE id = :id AND EXISTS (SELECT 1 FROM languoid WHERE pk = l.pk '
        'AND father_pk = (SELECT pk FROM language WHERE id = :before))', conn)
    move_uoid = sa.text('UPDATE languoid AS ll '
        'SET father_pk = (SELECT pk FROM language WHERE id = :after) '
        'WHERE EXISTS (SELECT 1 FROM language WHERE pk = ll.pk AND id = :id) '
        'AND father_pk = (SELECT pk FROM language WHERE id = :before)', conn)

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

    select_jd = sa.text('SELECT jsondata FROM language WHERE id = :id', conn)
    update_jd = sa.text('UPDATE language SET updated = now(), '
        'jsondata = :jsondata WHERE id = :id', conn)

    params = {'type': 'name', 'description': 'Glottolog', 'lang': 'en'}
    move_idents = sa.text('UPDATE languageidentifier AS li SET updated = now(), '
        'language_pk = u.language_pk FROM ('
        'SELECT pk, identifier_pk, (SELECT pk FROM language WHERE id = :after) AS language_pk '
        'FROM languageidentifier WHERE language_pk = (SELECT pk FROM language WHERE id = :before) '
        'AND EXISTS (SELECT 1 FROM language WHERE id = :before) '
        'AND EXISTS (SELECT 1 FROM language WHERE id = :after)) AS u '
        'WHERE li.pk = u.pk AND NOT EXISTS (SELECT 1 FROM languageidentifier '
        'WHERE identifier_pk = u.identifier_pk AND language_pk = u.language_pk) '
        'AND NOT EXISTS (SELECT 1 FROM identifier WHERE pk = u.identifier_pk '
            'AND type = :type AND description = :description AND lang = :lang '
            'AND name = (SELECT name FROM language WHERE id = :before))',
        conn).bindparams(**params)
    unlink_idents = sa.text('DELETE FROM languageidentifier AS li '
        'WHERE language_pk = (SELECT pk FROM language WHERE id = :before) '
        'AND EXISTS (SELECT 1 FROM language WHERE id = :before) '
        'AND EXISTS (SELECT 1 FROM language WHERE id = :after) '
        'AND NOT EXISTS (SELECT 1 FROM identifier WHERE pk = li.identifier_pk '
            'AND type = :type AND description = :description AND lang = :lang '
            'AND name = (SELECT name FROM language WHERE id = :before))',
        conn).bindparams(**params)
    copy_name = sa.text('INSERT INTO languageidentifier '
        '(created, updated, active, version, language_pk, identifier_pk) '
        'SELECT now(), now(), true, 1, '
        '(SELECT pk FROM language WHERE id = :after), '
        '(SELECT pk FROM identifier WHERE type = :type AND description = :description '
            'AND lang = :lang AND name = (SELECT name FROM language WHERE id = :before)) '
        'WHERE NOT EXISTS (SELECT 1 FROM languageidentifier '
        'WHERE language_pk = (SELECT pk FROM language WHERE id = :after) '
        'AND identifier_pk = (SELECT pk FROM identifier WHERE type = :type '
        'AND description = :description AND lang = :lang '
            'AND name = (SELECT name FROM language WHERE id = :before))) '
        'AND EXISTS (SELECT 1 FROM language WHERE id = :before) '
        'AND EXISTS (SELECT 1 FROM language WHERE id = :after)',
        conn).bindparams(**params)

    move_refs = sa.text('UPDATE languagesource AS ls SET updated = now(), '
        'language_pk = u.language_pk FROM ('
        'SELECT pk, source_pk, (SELECT pk FROM language WHERE id = :after) AS language_pk '
        'FROM languagesource WHERE language_pk = (SELECT pk FROM language WHERE id = :before) '
        'AND EXISTS (SELECT 1 FROM language WHERE id = :before) '
        'AND EXISTS (SELECT 1 FROM language WHERE id = :after)) AS u '
        'WHERE ls.pk = u.pk AND NOT EXISTS (SELECT 1 FROM languagesource '
        'WHERE source_pk = u.source_pk AND language_pk = u.language_pk)', conn)
    unlink_refs = sa.text('DELETE FROM languagesource AS ls '
        'WHERE language_pk = (SELECT pk FROM language WHERE id = :before) '
        'AND EXISTS (SELECT 1 FROM language WHERE id = :before) '
        'AND EXISTS (SELECT 1 FROM language WHERE id = :after)', conn)

    for id, before, after in MOVE:
        move_lang.execute(id=id, before=before)
        move_uoid.execute(id=id, before=before, after=after)

    for id, replacement in MERGE:
        lang_deactivate.execute(id=id)
        uoid_deactivate.execute(id=id)

        supersede.execute(id=id, replacement=replacement)
        
        new, old = (json.loads(select_jd.scalar(id=_) or '{}') for _ in (id, replacement))
        new.update(old)
        if new != old:
            update_jd.execute(id=id, jsondata=json.dumps(new))

        move_idents.execute(before=id, after=replacement)
        unlink_idents.execute(before=id, after=replacement)
        copy_name.execute(before=id, after=replacement)

        move_refs.execute(before=id, after=replacement)
        unlink_refs.execute(before=id, after=replacement)

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
