# coding=utf-8
"""fix source.description and source.pages_int

Revision ID: 184b209609c4
Revises: c80f2d77379
Create Date: 2014-06-20 09:32:06.040168

"""

# revision identifiers, used by Alembic.
revision = '184b209609c4'
down_revision = 'c80f2d77379'

import datetime

from alembic import op
import sqlalchemy as sa

from glottolog3.scripts.util import compute_pages


def upgrade():
    conn = op.get_bind()
    tmpl = """\
update source set description = {0} where description is null and {0} is not null"""
    for col in 'title booktitle'.split():
        conn.execute(tmpl.format(col))

    for row in list(conn.execute(
            "select pk, pages, pages_int, startpage_int from source where pages_int < 0")):
        pk, pages, number, start = row
        _start, _end, _number = compute_pages(pages)
        if _number > 0 and _number != number:
            conn.execute(
                "update source set pages_int = %s, startpage_int = %s where pk = %s",
                (_number, _start, pk))
            conn.execute(
                "update ref set endpage_int = %s where pk = %s",
                (_end, pk))


def downgrade():
    pass
