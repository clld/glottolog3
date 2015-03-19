# coding=utf-8
"""name changes

Revision ID: 333ceef01d8e
Revises: f17360a2b38
Create Date: 2015-03-19 11:21:31.657000

"""

# revision identifiers, used by Alembic.
revision = '333ceef01d8e'
down_revision = 'f17360a2b38'

import datetime

from alembic import op
import sqlalchemy as sa

GCODE_OLD_NEW = [
    ('chhi1245', u'Chhintange', u'Chintang'),
    ('gugu1255', u'Guguyimidjir', u'Guugu Yimidhirr'),
    ('hupd1244', u'Hupde', u'Hup'),
    ('lush1249', u'Lushai', u'Mizo'),
    ('maib1239', u'Mai Brat', u'Maybrat'),
    ('mart1255', u'Martuyhunira', u'Martuthunira'),
    ('sanm1287', u'San Mateo Del Mar Huave', u'San Mateo del Mar Huave'),
    ('yuca1254', u'Yucateco', u'Yucatec Maya'),
    ('valm1241', u'Valman', u'Walman'),
    ('bang1363', u'Bangi Me', u'Bangime'),
    ('ghul1238', u'Ghulfan', u'Uncunwee'),
    ('kara1489', u'Karaga Mandaya', u'Mandaya'),
    ('moni1237', u'Monimbo', u'Mangue'),
    ('darm1243', u'Darmiya', u'Darma'),
    ('dido1241', u'Dido', u'Tsez'),
    ('ghod1238', u'Ghodoberi', u'Godoberi'),
    ('gily1242', u'Gilyak', u'Nivkh'),
    ('chin1272', u'Chinook jargon', u'Chinuk Wawa'),
    ('chuk1273', u'Chukot', u'Chukchi'),
    ('colo1256', u'Colorado', u'Tsafiki'),
    ('copa1236', u'Copainala Zoque', u'Copainal\xe1 Zoque'),
    ('daur1238', u'Daur', u'Dagur'),
    ('east2440', u'East Makian', u'Taba'),
    ('east2544', u'Eastern Abnaki', u'Eastern Abenaki'),
    ('west2630', u'Western Abnaki', u'Western Abenaki'),
    ('yiry1247', u'Yir Yoront', u'Yir-Yoront'),
    ('zagh1240', u'Zaghawa', u'Beria'),
    ('kani1282', u'Kaniet', u'Southern Kaniet'),
    ('kani1283', u'Kaniet-Dempwolff', u'Northern Kaniet'),
    ('oldi1245', u'Old Irish (to 900)', u'Old Irish'),
    ('aeka1244', u'Aeka (orokaivic)', u'Aeka (Orokaivan)'),
    ('kana1286', u'Kanakanabu', u'Kanakanavu'),
    ('amar1271', u'Amarag', u'Amurdak'),
    ('anei1239', u'Aneityum', u'Anejom'),
    ('onaa1245', u'Ona', u'Selknam'),
    ('fana1235', u'Fanagalo', u'Fanakalo'),
    ('bira1253', u'Birale', u'Ongota'),
    ('cacu1241', u'Cacua', u'Kakua'),
    ('nuka1242', u'Nukak Maku', u'Nukak'),
    ('hari1246', u'Harijan Kinnauri', u'Pahari Kinnauri'),
    ('tokh1242', u'Tokharian A', u'Tocharian A'),
    ('tokh1243', u'Tokharian B', u'Tocharian B'),
    ('nucl1235', u'Nuclear Armenian', u'Modern Armenian'),
    ('nucl1302', u'Nuclear Georgian', u'Modern Georgian'),
    ('nucl1305', u'Nuclear Kannada', u'Modern Kannada'),
    ('kagf1238', u'Kag-Fer-Jiir-Koor-Ror-Us-Zuksun', u"Ut-Ma'in"),
    ('chur1257', u'Church Slavic', u'Old Church Slavonic'),
    ('orej1242', u'Orejon', u'Maihiki'),
    ('abis1238', u'Abishira', u'Aewa'),
    ('hovo1239', u'Hovongan', u'Hobongan'),
]


def upgrade():
    update_name = sa.text('UPDATE language SET updated = now(), '
        'name = :after WHERE id = :id AND name = :before')

    insert_ident = sa.text('INSERT INTO identifier '
        '(created, updated, active, version, type, description, lang, name) '
        'SELECT now(), now(), true, 1, :type, :description, :lang, :name '
        'WHERE NOT EXISTS (SELECT 1 FROM identifier WHERE type = :type '
        'AND description = :description AND lang = :lang AND name = :name)'
        ).bindparams(type='name', description='Glottolog', lang='en')

    insert_lang_ident = sa.text('INSERT INTO languageidentifier '
        '(created, updated, active, version, language_pk, identifier_pk) '
        'SELECT now(), now(), true, 1, '
        '(SELECT pk FROM language WHERE id = :id), '
        '(SELECT pk FROM identifier WHERE type = :type '
        'AND description = :description AND lang = :lang AND name = :name) '
        'WHERE NOT EXISTS (SELECT 1 FROM languageidentifier '
        'WHERE language_pk = (SELECT pk FROM language WHERE id = :id) '
        'AND identifier_pk = (SELECT pk FROM identifier WHERE type = :type '
        'AND description = :description AND lang = :lang AND name = :name))'
        ).bindparams(type='name', description='Glottolog', lang='en')

    for id, before, after in GCODE_OLD_NEW:
        op.execute(update_name.bindparams(id=id, before=before, after=after))
        op.execute(insert_ident.bindparams(name=after))
        op.execute(insert_lang_ident.bindparams(id=id, name=after))


def downgrade():
    pass
