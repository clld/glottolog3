# coding=utf-8
"""Glottolog Curator

Revision ID: 3f325e2fa551
Revises: 5113368c7dbe
Create Date: 2013-09-07 15:36:17.837789

"""

# revision identifiers, used by Alembic.
revision = '3f325e2fa551'
down_revision = '5113368c7dbe'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    # from glottologcurator
    conn = op.get_bind()
    for sql, params in [
    ("""INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk""", {u'updated': datetime.datetime(2013, 9, 7, 13, 35, 4, 811037), u'created': datetime.datetime(2013, 9, 7, 13, 35, 4, 811031), u'object_pk': 36911, u'jsondata': None, u'version': 1, u'value': u'Fixed error due to data migration.', u'key': u'_gc_comment_', u'active': True, u'ord': 1}),
    ("""UPDATE languoid SET father_pk=%(father_pk)s WHERE languoid.pk = %(languoid_pk)s""", {u'father_pk': 36816, u'languoid_pk': 36911}),
    ("""INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk""", {u'updated': datetime.datetime(2013, 9, 7, 13, 35, 26, 449095), u'created': datetime.datetime(2013, 9, 7, 13, 35, 26, 449089), u'object_pk': 36913, u'jsondata': None, u'version': 1, u'value': u'Fixed error due to data migration.', u'key': u'_gc_comment_', u'active': True, u'ord': 1}),
    ("""UPDATE languoid SET father_pk=%(father_pk)s WHERE languoid.pk = %(languoid_pk)s""", {u'father_pk': 36816, u'languoid_pk': 36913}),
    ("""INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk""", {u'updated': datetime.datetime(2013, 9, 7, 13, 35, 49, 802965), u'created': datetime.datetime(2013, 9, 7, 13, 35, 49, 802959), u'object_pk': 36910, u'jsondata': None, u'version': 1, u'value': u'Fixed error due to data migration.', u'key': u'_gc_comment_', u'active': True, u'ord': 1}),
    ("""UPDATE languoid SET father_pk=%(father_pk)s WHERE languoid.pk = %(languoid_pk)s""", {u'father_pk': 36816, u'languoid_pk': 36910}),
    ]:
        conn.execute(sql, params)


def downgrade():
    pass

