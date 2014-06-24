# coding=utf-8
"""glottologcurator

Revision ID: 10acd02fac9a
Revises: baf6409f1f7
Create Date: 2014-06-20 13:39:30.560157

"""

# revision identifiers, used by Alembic.
revision = '10acd02fac9a'
down_revision = 'baf6409f1f7'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()
    return
    for sql, params in [
        (u'UPDATE languoid SET father_pk=%(father_pk)s WHERE languoid.pk = %(languoid_pk)s',
         {'father_pk': 104782, 'languoid_pk': 36803}),
        (u'UPDATE language SET updated=%(updated)s, name=%(name)s WHERE language.pk = %(language_pk)s',
         {'updated': datetime.datetime(2013, 12, 3, 9, 51, 33, 856599), 'name': u'Kryz', 'language_pk': 35943}),

        # TODO: check existence of identifier:
        (u'INSERT INTO languageidentifier (created, updated, active, jsondata, language_pk, identifier_pk, description, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(language_pk)s, %(identifier_pk)s, %(description)s, %(version)s) RETURNING languageidentifier.pk',
         {'updated': datetime.datetime(2013, 12, 3, 9, 51, 34, 268289), 'version': 1, 'description': None, 'created': datetime.datetime(2013, 12, 3, 9, 51, 34, 268278), 'active': True, 'identifier_pk': 152013, 'language_pk': 35943, 'jsondata': None}),
        (u'DELETE FROM languageidentifier WHERE languageidentifier.pk = %(pk)s', 
         {'pk': 154862}),

        (u'UPDATE language SET updated=%(updated)s, name=%(name)s WHERE language.pk = %(language_pk)s',
         {'updated': datetime.datetime(2013, 12, 3, 9, 55, 24, 453513), 'name': u'Manange', 'language_pk': 27015}),
        # TODO: check: should this insert the new name as Glottolog name identifier?
        (u'INSERT INTO identifier (created, updated, active, jsondata, name, description, markup_description, id, type, lang, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(name)s, %(description)s, %(markup_description)s, %(id)s, %(type)s, %(lang)s, %(version)s) RETURNING identifier.pk',
         {'updated': datetime.datetime(2013, 12, 3, 9, 55, 24, 461306), 'markup_description': None, 'active': True, 'id': None, 'description': u'', 'lang': u'en', 'name': u'', 'created': datetime.datetime(2013, 12, 3, 9, 55, 24, 461295), 'jsondata': None, 'version': 1, 'type': u'name'}),

        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk',
         {'updated': datetime.datetime(2013, 12, 4, 13, 27, 48, 531985), 'version': 1, 'jsondata': None, 'key': u'pronunciation', 'created': datetime.datetime(2013, 12, 4, 13, 27, 48, 531971), 'active': True, 'object_pk': 26717, 'ord': 1, 'value': u"[m\u0259s'kougi\u0259n] or [m\u0259sko'gi:\u0259n]"}),

        (u'INSERT INTO identifier (created, updated, active, jsondata, name, description, markup_description, id, type, lang, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(name)s, %(description)s, %(markup_description)s, %(id)s, %(type)s, %(lang)s, %(version)s) RETURNING identifier.pk',
         {'updated': datetime.datetime(2013, 12, 4, 13, 37, 57, 648218), 'markup_description': None, 'active': True, 'id': None, 'description': u'', 'lang': u'en', 'name': u'Narua', 'created': datetime.datetime(2013, 12, 4, 13, 37, 57, 648205), 'jsondata': None, 'version': 1, 'type': u'ethnologue'}),
        (u'INSERT INTO languageidentifier (created, updated, active, jsondata, language_pk, identifier_pk, description, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(language_pk)s, %(identifier_pk)s, %(description)s, %(version)s) RETURNING languageidentifier.pk', 
         {'updated': datetime.datetime(2013, 12, 4, 13, 37, 57, 689167), 'version': 1, 'description': None, 'created': datetime.datetime(2013, 12, 4, 13, 37, 57, 689155), 'active': True, 'identifier_pk': 152014, 'language_pk': 27774, 'jsondata': None}),

        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk',
         {'updated': datetime.datetime(2013, 12, 4, 13, 37, 57, 703470), 'version': 1, 'jsondata': None, 'key': u'speakers', 'created': datetime.datetime(2013, 12, 4, 13, 37, 57, 703458), 'active': True, 'object_pk': 27774, 'ord': 1, 'value': u'40,000 (estimated) (Lidz 2010: 3, based on Yang 2009)'}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2013, 12, 4, 13, 40, 54, 498064), 'version': 1, 'jsondata': None, 'key': u'location', 'created': datetime.datetime(2013, 12, 4, 13, 40, 54, 498051), 'active': True, 'object_pk': 27774, 'ord': 1, 'value': u'Yunnan, Sichuan (China)'}),

        (u'UPDATE language SET updated=%(updated)s, name=%(name)s WHERE language.pk = %(language_pk)s',
         {'updated': datetime.datetime(2013, 12, 12, 11, 8, 43, 106837), 'language_pk': 35881, 'name': u'Avar'}),

        # three proposals for name changes:
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk',
         {'updated': datetime.datetime(2014, 1, 19, 13, 12, 13, 799981), 'version': 1, 'jsondata': None, 'key': u'New primary name', 'created': datetime.datetime(2014, 1, 19, 13, 12, 13, 799970), 'active': True, 'object_pk': 40741, 'ord': 1, 'value': u'Keo'}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 1, 19, 13, 12, 13, 812645), 'version': 1, 'value': u'"Keo" is the name form used by Baird (2008) (in Senft (ed.))', 'key': u'_gc_comment_', 'created': datetime.datetime(2014, 1, 19, 13, 12, 13, 812634), 'active': True, 'object_pk': 40741, 'ord': 1, 'jsondata': None}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 1, 19, 13, 18, 7, 983953), 'version': 1, 'jsondata': None, 'key': u'New primary name', 'created': datetime.datetime(2014, 1, 19, 13, 18, 7, 983943), 'active': True, 'object_pk': 34418, 'ord': 1, 'value': u'Kotiria'}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 1, 19, 13, 18, 7, 996024), 'version': 1, 'value': u'According to Stenzel (2013:1), "Wanano" is a name given by unknown outsiders and its use has been called into question by village leaders ansd the directors, teachers and students of the indigenous school. In 2006, the group publicly adopted the policy of using exclusively their own traditional name Kotiria \'water people\' to refer to themselves and to their language and have requested that the outsiders working with them do the same."', 'key': u'_gc_comment_', 'created': datetime.datetime(2014, 1, 19, 13, 18, 7, 996011), 'active': True, 'object_pk': 34418, 'ord': 1, 'jsondata': None}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 1, 19, 13, 20, 42, 737308), 'version': 1, 'jsondata': None, 'key': u'New primary name', 'created': datetime.datetime(2014, 1, 19, 13, 20, 42, 737297), 'active': True, 'object_pk': 34417, 'ord': 1, 'value': u"Wa'ikhana"}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 1, 19, 13, 20, 42, 738612), 'version': 1, 'value': u'The Wa\'ikhana have adopted the policy of using the name "Wa\'ikhana" rather than "Piratapuyo".', 'key': u'_gc_comment_', 'created': datetime.datetime(2014, 1, 19, 13, 20, 42, 738603), 'active': True, 'object_pk': 34417, 'ord': 1, 'jsondata': None}),

        (u'DELETE FROM languageidentifier WHERE languageidentifier.pk = %(pk)s',
         {'pk': 97448}),

        # more proposals for new names:
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk',
         {'updated': datetime.datetime(2014, 1, 19, 13, 23, 28, 856365), 'version': 1, 'jsondata': None, 'key': u'New primary name', 'created': datetime.datetime(2014, 1, 19, 13, 23, 28, 856354), 'active': True, 'object_pk': 35943, 'ord': 1, 'value': u'Kryz'}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 1, 19, 13, 23, 28, 866914), 'version': 1, 'value': u'The name form "Kryz" corresponds best to Russian "\u043a\u0440\u044b\u0437\u0441\u043a\u0438\u0439 \u044f\u0437\u044b\u043a", and is used by Authier (2000).', 'key': u'_gc_comment_', 'created': datetime.datetime(2014, 1, 19, 13, 23, 28, 866904), 'active': True, 'object_pk': 35943, 'ord': 1, 'jsondata': None}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 1, 19, 13, 27, 37, 274389), 'version': 1, 'jsondata': None, 'key': u'New primary name', 'created': datetime.datetime(2014, 1, 19, 13, 27, 37, 274379), 'active': True, 'object_pk': 38851, 'ord': 1, 'value': u'Malacca-Batavia Creole'}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 1, 19, 13, 27, 37, 281525), 'version': 1, 'value': u'The Portuguese-based creole varieties of Malacca (Malaysia) and Batavia (now Jakarta, Indonesia) are so similar that they are treated as a single language in Glottolog.', 'key': u'_gc_comment_', 'created': datetime.datetime(2014, 1, 19, 13, 27, 37, 281515), 'active': True, 'object_pk': 38851, 'ord': 1, 'jsondata': None}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 1, 19, 13, 29, 24, 885895), 'version': 1, 'jsondata': None, 'key': u'New primary name', 'created': datetime.datetime(2014, 1, 19, 13, 29, 24, 885885), 'active': True, 'object_pk': 24290, 'ord': 1, 'value': u'Yeri'}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 1, 19, 13, 29, 24, 887281), 'version': 1, 'value': u'The name "Yeri" is used by Jennifer Wilson (U Buffalo, MPI-EVA Leipzig), actively working on the language (2014).', 'key': u'_gc_comment_', 'created': datetime.datetime(2014, 1, 19, 13, 29, 24, 887272), 'active': True, 'object_pk': 24290, 'ord': 1, 'jsondata': None}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 1, 19, 13, 33, 27, 219665), 'version': 1, 'jsondata': None, 'key': u'New primary name', 'created': datetime.datetime(2014, 1, 19, 13, 33, 27, 219656), 'active': True, 'object_pk': 23775, 'ord': 1, 'value': u'Lokono'}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 1, 19, 13, 33, 27, 220961), 'version': 1, 'value': u'The name "Lokono" seems to be preferred by linguists working on the language (e.g. Konrad Rybka).', 'key': u'_gc_comment_', 'created': datetime.datetime(2014, 1, 19, 13, 33, 27, 220954), 'active': True, 'object_pk': 23775, 'ord': 1, 'jsondata': None}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 1, 20, 15, 33, 13, 374244), 'version': 1, 'jsondata': None, 'key': u'New primary name', 'created': datetime.datetime(2014, 1, 20, 15, 33, 13, 374234), 'active': True, 'object_pk': 35965, 'ord': 1, 'value': u'Anykh'}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 1, 20, 15, 33, 13, 375808), 'version': 1, 'value': u'The name form "Anyx" uses the IPA value of "x".', 'key': u'_gc_comment_', 'created': datetime.datetime(2014, 1, 20, 15, 33, 13, 375799), 'active': True, 'object_pk': 35965, 'ord': 1, 'jsondata': None}),

        # new primary and additional name:
        (u'UPDATE language SET updated=%(updated)s, name=%(name)s WHERE language.pk = %(language_pk)s',
         {'updated': datetime.datetime(2014, 2, 27, 9, 49, 25, 840171), 'name': u'Chinese Pidgin Russian', 'language_pk': 104770}),
        (u'INSERT INTO identifier (created, updated, active, jsondata, name, description, markup_description, id, type, lang, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(name)s, %(description)s, %(markup_description)s, %(id)s, %(type)s, %(lang)s, %(version)s) RETURNING identifier.pk',
         {'updated': datetime.datetime(2014, 2, 27, 9, 49, 26, 72770), 'markup_description': None, 'active': True, 'id': None, 'description': u'Wikipedia', 'lang': u'en', 'name': u'Kyakhta Russian\u2013Chinese Pidgin', 'created': datetime.datetime(2014, 2, 27, 9, 49, 26, 72756), 'jsondata': None, 'version': 1, 'type': u'name'}),
        (u'INSERT INTO languageidentifier (created, updated, active, jsondata, language_pk, identifier_pk, description, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(language_pk)s, %(identifier_pk)s, %(description)s, %(version)s) RETURNING languageidentifier.pk', 
         {'updated': datetime.datetime(2014, 2, 27, 9, 49, 26, 156472), 'version': 1, 'description': None, 'created': datetime.datetime(2014, 2, 27, 9, 49, 26, 156461), 'active': True, 'identifier_pk': 152015, 'language_pk': 104770, 'jsondata': None}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk',
         {'updated': datetime.datetime(2014, 2, 27, 9, 49, 26, 258261), 'version': 1, 'value': u'Chinese Pidgin Russian is also called "Kyakhta Pidgin" because of its prominence in the town of Kyakhta.', 'key': u'name comment', 'created': datetime.datetime(2014, 2, 27, 9, 49, 26, 258252), 'active': True, 'object_pk': 104770, 'ord': 1, 'jsondata': None}),

        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk',
         {'updated': datetime.datetime(2014, 2, 27, 9, 52, 26, 290443), 'version': 1, 'value': u'The Wa\'ikhana have adopted the policy of using the name "Wa\'ikhana" rather than "Piratapuyo".', 'key': u'name comment', 'created': datetime.datetime(2014, 2, 27, 9, 52, 26, 290434), 'active': True, 'object_pk': 34417, 'ord': 1, 'jsondata': None}),
        (u'UPDATE language SET updated=%(updated)s, name=%(name)s WHERE language.pk = %(language_pk)s',
         {'updated': datetime.datetime(2014, 2, 27, 9, 53, 19, 386251), 'name': u"Wa'ikhana", 'language_pk': 34417}),
        (u'UPDATE language SET updated=%(updated)s, name=%(name)s WHERE language.pk = %(language_pk)s',
         {'updated': datetime.datetime(2014, 2, 27, 10, 1, 2, 850592), 'name': u'Jeli', 'language_pk': 26124}),
        (u'DELETE FROM languageidentifier WHERE languageidentifier.pk = %(pk)s', 
         {'pk': 160013}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 2, 27, 10, 1, 2, 903794), 'version': 1, 'value': u'Ethnologue\'s name\'s name follows *181522*, but Glottolog adopts the name "Jeli" from *141802*.', 'key': u'name comment', 'created': datetime.datetime(2014, 2, 27, 10, 1, 2, 903783), 'active': True, 'object_pk': 26124, 'ord': 1, 'jsondata': None}),
        (u'UPDATE language SET updated=%(updated)s, name=%(name)s WHERE language.pk = %(language_pk)s',
         {'updated': datetime.datetime(2014, 2, 27, 10, 6, 14, 545170), 'name': u'Ancient Greek', 'language_pk': 36680}),
        (u'DELETE FROM languageidentifier WHERE languageidentifier.pk = %(pk)s', 
         {'pk': 166552}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 2, 27, 10, 6, 14, 605908), 'version': 1, 'value': u'This refers to the Greek language in Antiquity and in the Middle Ages, until the end of the Byzantine empire.', 'key': u'name comment', 'created': datetime.datetime(2014, 2, 27, 10, 6, 14, 605898), 'active': True, 'object_pk': 36680, 'ord': 1, 'jsondata': None}),
        (u'UPDATE language SET updated=%(updated)s, name=%(name)s WHERE language.pk = %(language_pk)s',
         {'updated': datetime.datetime(2014, 2, 28, 15, 0, 53, 732273), 'name': u'Lokono', 'language_pk': 23775}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 2, 28, 15, 0, 53, 774305), 'version': 1, 'value': u'The name "Lokono" seems to be preferred by linguists working on the language (e.g. Konrad Rybka). It also has the advantage that it cannot be confused with the name of the family (Arawakan).', 'key': u'Name comment', 'created': datetime.datetime(2014, 2, 28, 15, 0, 53, 774293), 'active': True, 'object_pk': 23775, 'ord': 1, 'jsondata': None}),
        (u'UPDATE language SET updated=%(updated)s, name=%(name)s WHERE language.pk = %(language_pk)s',
         {'updated': datetime.datetime(2014, 2, 28, 15, 1, 48, 908371), 'name': u'Anykh', 'language_pk': 35965}),
        (u'DELETE FROM languageidentifier WHERE languageidentifier.pk = %(pk)s', 
         {'pk': 135859}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 2, 28, 15, 1, 48, 953516), 'version': 1, 'value': u'The name form "Anyx" uses the IPA value of "x".', 'key': u'Name comment', 'created': datetime.datetime(2014, 2, 28, 15, 1, 48, 953507), 'active': True, 'object_pk': 35965, 'ord': 1, 'jsondata': None}),
        (u'DELETE FROM language_data WHERE language_data.pk = %(pk)s',
         {'pk': 26}),
        (u'UPDATE language SET updated=%(updated)s, name=%(name)s WHERE language.pk = %(language_pk)s', 
         {'updated': datetime.datetime(2014, 2, 28, 15, 35, 18, 488073), 'name': u'Malacca-Batavia Creole', 'language_pk': 38851}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 2, 28, 15, 35, 18, 527252), 'version': 1, 'value': u'The Portuguese-based creole varieties of Malacca (Malaysia) and Batavia (now Jakarta, Indonesia) are so similar that they are treated as a single language in Glottolog.', 'key': u'Name comment', 'created': datetime.datetime(2014, 2, 28, 15, 35, 18, 527243), 'active': True, 'object_pk': 38851, 'ord': 1, 'jsondata': None}),
        (u'DELETE FROM language_data WHERE language_data.pk = %(pk)s',
         {'pk': 20}),
        (u'UPDATE language SET updated=%(updated)s, name=%(name)s WHERE language.pk = %(language_pk)s', 
         {'updated': datetime.datetime(2014, 2, 28, 15, 43, 13, 246561), 'name': u'Khwarshi', 'language_pk': 35875}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk',
         {'updated': datetime.datetime(2014, 2, 28, 15, 45, 38, 225309), 'version': 1, 'value': u'"Manange" is the form of the language name used by Kristine Hildebrandt.', 'key': u'Name comment', 'created': datetime.datetime(2014, 2, 28, 15, 45, 38, 225298), 'active': True, 'object_pk': 27015, 'ord': 1, 'jsondata': None}),

        (u'INSERT INTO identifier (created, updated, active, jsondata, name, description, markup_description, id, type, lang, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(name)s, %(description)s, %(markup_description)s, %(id)s, %(type)s, %(lang)s, %(version)s) RETURNING identifier.pk',
         {'updated': datetime.datetime(2014, 2, 28, 15, 47, 25, 909390), 'markup_description': None, 'active': True, 'id': None, 'description': u'Glottolog', 'lang': u'en', 'name': u'Wix\xe1rika', 'created': datetime.datetime(2014, 2, 28, 15, 47, 25, 909381), 'jsondata': None, 'version': 1, 'type': u'name'}),
        (u'INSERT INTO languageidentifier (created, updated, active, jsondata, language_pk, identifier_pk, description, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(language_pk)s, %(identifier_pk)s, %(description)s, %(version)s) RETURNING languageidentifier.pk', 
         {'updated': datetime.datetime(2014, 2, 28, 15, 47, 25, 931309), 'version': 1, 'description': None, 'created': datetime.datetime(2014, 2, 28, 15, 47, 25, 931299), 'active': True, 'identifier_pk': 152016, 'language_pk': 34671, 'jsondata': None}),

        (u'UPDATE language SET updated=%(updated)s, name=%(name)s WHERE language.pk = %(language_pk)s',
         {'updated': datetime.datetime(2014, 2, 28, 15, 49, 19, 371446), 'name': u'Hinuq', 'language_pk': 35880}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 2, 28, 15, 49, 19, 408992), 'version': 1, 'value': u'The name form "Hinuq" is used by Diana Forker.', 'key': u'Name comment', 'created': datetime.datetime(2014, 2, 28, 15, 49, 19, 408983), 'active': True, 'object_pk': 35880, 'ord': 1, 'jsondata': None}),

        (u'UPDATE language SET updated=%(updated)s, name=%(name)s WHERE language.pk = %(language_pk)s',
         {'updated': datetime.datetime(2014, 2, 28, 15, 52, 53, 561488), 'name': u'Iwaidjic', 'language_pk': 104972}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 2, 28, 15, 52, 53, 608398), 'version': 1, 'value': u'Ethnologue calls the family "Yiwaidjic", but the name of the language is "Iwaidja", so we use "Iwaidjic".', 'key': u'Name comment', 'created': datetime.datetime(2014, 2, 28, 15, 52, 53, 608389), 'active': True, 'object_pk': 104972, 'ord': 1, 'jsondata': None}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 2, 28, 15, 52, 53, 609447), 'version': 1, 'value': u'\u201cIwaidjan Proper\u201d is not a good name of a family. Should be renamed to \u201cIwaidjic\u201d (cf. Ethnologue\u2019s Yiwaidjic)', 'key': u'_gc_comment_', 'created': datetime.datetime(2014, 2, 28, 15, 52, 53, 609440), 'active': True, 'object_pk': 104972, 'ord': 1, 'jsondata': None}),

        (u'UPDATE language SET updated=%(updated)s, name=%(name)s WHERE language.pk = %(language_pk)s',
         {'updated': datetime.datetime(2014, 2, 28, 15, 53, 59, 813199), 'name': u'Jaminjung', 'language_pk': 36395}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 2, 28, 15, 53, 59, 852224), 'version': 1, 'value': u'Eva Schultze-Berndt uses "Jaminjung".', 'key': u'Name comment', 'created': datetime.datetime(2014, 2, 28, 15, 53, 59, 852215), 'active': True, 'object_pk': 36395, 'ord': 1, 'jsondata': None}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 2, 28, 15, 53, 59, 853291), 'version': 1, 'value': u'internal comment', 'key': u'_gc_comment_', 'created': datetime.datetime(2014, 2, 28, 15, 53, 59, 853283), 'active': True, 'object_pk': 36395, 'ord': 1, 'jsondata': None}),

        (u'UPDATE language SET updated=%(updated)s, name=%(name)s WHERE language.pk = %(language_pk)s',
         {'updated': datetime.datetime(2014, 2, 28, 15, 55, 37, 389077), 'name': u'Jaminjungan', 'language_pk': 36393}),
        (u'DELETE FROM languageidentifier WHERE languageidentifier.pk = %(pk)s', 
         {'pk': 119730}),
        (u'INSERT INTO language_data (created, updated, active, jsondata, key, value, ord, object_pk, version) VALUES (%(created)s, %(updated)s, %(active)s, %(jsondata)s, %(key)s, %(value)s, %(ord)s, %(object_pk)s, %(version)s) RETURNING language_data.pk', 
         {'updated': datetime.datetime(2014, 2, 28, 15, 55, 37, 431485), 'version': 1, 'value': u'The language is called "Jaminjung", so the family should be called "Jaminjungan".', 'key': u'_gc_comment_', 'created': datetime.datetime(2014, 2, 28, 15, 55, 37, 431475), 'active': True, 'object_pk': 36393, 'ord': 1, 'jsondata': None}),
    ]:
        conn.execute(sql, params)


def downgrade():
    pass

