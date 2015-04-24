# coding=utf-8
"""move retired bookkeeping

Revision ID: 3d8925dd5250
Revises: 184c40fb1702
Create Date: 2015-04-24 13:22:34.719000

"""

# revision identifiers, used by Alembic.
revision = '3d8925dd5250'
down_revision = '184c40fb1702'

import datetime

from alembic import op
import sqlalchemy as sa

AFTER = 'book1242'

MOVE = [  # 106
    'aari1244', 'adze1241', 'ahea1240', 'aiku1240', 'amap1241',
    'amer1256', 'amik1238', 'araf1244', 'arak1256', 'atue1238',
    'auve1240', 'baha1262', 'baku1265', 'bana1306', 'belg1241',
    'beng1290', 'bera1267', 'bisu1247', 'buxi1237', 'buya1247',
    'caru1240', 'chit1285', 'dara1255', 'daya1245', 'enim1238',
    'euro1250', 'fala1245', 'garr1261', 'gasc1241', 'gema1236',
    'hmon1338', 'ipek1240', 'itut1240', 'izer1243', 'jaru1257',
    'kaha1240', 'kahu1242', 'kati1278', 'kaya1334', 'kayu1244',
    'khia1237', 'koho1245', 'krui1237', 'kunf1238', 'lach1251',
    'lahu1255', 'land1262', 'lang1334', 'lema1244', 'limo1250',
    'lint1237', 'lowe1441', 'mada1299', 'maha1308', 'mala1546',
    'mimi1246', 'moin1242', 'muji1236', 'muko1237', 'mund1339',
    'nava1245', 'nort3249', 'nort3250', 'nort3251', 'nyad1241',
    'occi1241', 'ogan1237', 'oldp1255', 'orok1270', 'pale1264',
    'pamo1255', 'patl1234', 'pene1237', 'prov1247', 'pubi1237',
    'pula1268', 'puwa1234', 'rajb1244', 'rana1249', 'rawa1268',
    'saka1300', 'sara1350', 'sela1262', 'seme1248', 'sera1272',
    'silt1241', 'sind1280', 'siza1240', 'soul1243', 'sout3221',
    'sout3222', 'sout3223', 'sout3224', 'sout3225', 'suba1254',
    'sung1271', 'tanj1248', 'tarp1241', 'tlal1234', 'tomy1239',
    'tuto1242', 'uppe1459', 'west2863', 'wume1236', 'ying1248',
    'yuan1242',
]


def upgrade():
    move_lang = sa.text('UPDATE language AS l SET updated = now() '
        'WHERE id = :id AND EXISTS (SELECT 1 FROM languoid WHERE pk = l.pk '
        'AND father_pk IS NULL)')
    move_uoid = sa.text('UPDATE languoid AS ll '
        'SET father_pk = (SELECT pk FROM language WHERE id = :after) '
        'WHERE EXISTS (SELECT 1 FROM language WHERE pk = ll.pk AND id = :id) '
        'AND father_pk IS NULL')

    for id in MOVE:
        op.execute(move_lang.bindparams(id=id))
        op.execute(move_uoid.bindparams(id=id, after=AFTER))

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
