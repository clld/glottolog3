# coding=utf-8
"""retired yiy comment

Revision ID: 56616ae95a23
Revises: 3dfa2e32c21e
Create Date: 2014-11-18 10:11:59.696000

"""

# revision identifiers, used by Alembic.

revision = '56616ae95a23'
down_revision = '3dfa2e32c21e'

import datetime
import json

from alembic import op
import sqlalchemy as sa

BEFORE = 'http://www-01.sil.org/iso639-3/cr_files/2012-117.pdf'
AFTER = 'Yirrk-Mel is currently listed as an dialect of Yir Yoront (yiy), but it is clear they share a sister language relationship, but a dialectal one. Barry (2004), in his comparative historical linguistics work mentions "[proto Yirr], the common ancestor of Yir-Yoront and Yirrk-Mel" (389). The 2010 publication "Western Paman Languages" includes Yirrk-Mel (under its alternate name Yirrk-Thangalkl) as a sister language of Yir-Yoront. The AusAnthrop database lists them as two separate language entries. In addition, Dr. Claire Bowern has done recent fieldwork in the area and provided us with exact centroid coordinates of the area where the languages are spoken (see appropriate New Code Request form), and although extrapolating language relationship from geographical proximity is sometimes dangerous the two distinct sets of centroid coordinates in this case supports the claim that the languages are separate.'


def upgrade():
    conn = op.get_bind()
    select_json = sa.text('SELECT jsondata FROM language WHERE id = :id', conn)
    update_json = sa.text('UPDATE language SET updated = now(), jsondata = :jsondata '
        'WHERE id = :id', conn)

    jsondata = json.loads(select_json.scalar(id='yiry1245'))
    if jsondata.get('iso_retirement', {}).get('comment') == BEFORE:
        jsondata['iso_retirement']['comment'] = AFTER
        update_json.execute(id='yiry1245', jsondata=json.dumps(jsondata))


def downgrade():
    pass
