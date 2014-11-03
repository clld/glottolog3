# coding=utf-8

"""multitree unique

Revision ID: 1fd38a400cf6
Revises: 5a78dba481df
Create Date: 2014-11-03 16:31:54.597000

"""

# revision identifiers, used by Alembic.

revision = '1fd38a400cf6'
down_revision = '5a78dba481df'

import datetime
import json

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()

    target = sa.text('SELECT type, name, description, lang, '
        'array_agg(pk order by pk) as pks '
        'FROM identifier WHERE description IS NULL '
        'GROUP BY type, name, description, lang '
        'HAVING count(*) > 1 ORDER BY type, name', conn)

    update_lang_ident = sa.text('UPDATE languageidentifier SET updated = now(), '
        'identifier_pk = :after WHERE identifier_pk = ANY(:before)', conn)
    del_ident = sa.text('DELETE FROM identifier WHERE pk = ANY(:before)', conn)

    for type, name, description, lang, pks in target.execute():
        after, before = pks[0], pks[1:]
        update_lang_ident.execute(after=after, before=before)
        del_ident.execute(before=before)


def downgrade():
    pass
