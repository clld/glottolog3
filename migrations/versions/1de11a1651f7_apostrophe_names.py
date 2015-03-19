# coding=utf-8
"""apostrophe names

Revision ID: 1de11a1651f7
Revises: 333ceef01d8e
Create Date: 2015-03-19 11:24:26.560000

"""

# revision identifiers, used by Alembic.
revision = '1de11a1651f7'
down_revision = '333ceef01d8e'

import datetime

from alembic import op
import sqlalchemy as sa

GCODE_OLD_NEW = [
    ('hawa1246', u'Hawai\u2019i Creole', u"Hawai'i Creole"),
    ('koyo1243', u'Koyo (Cote d\u2019Ivoire)', u"Koyo (Cote d'Ivoire)"),
    ('kule1242', u'Kulere (Cote d\u2019Ivoire)', u"Kulere (Cote d'Ivoire)"),
    ('norf1242', u'Norf\u2019k-Pitkern', u"Norf'k-Pitkern"),
    ('norf1243', u'Norf\u2019k', u"Norf'k"),
    ('nucl1412', u'Nuclear Kwa\u2019', u"Nuclear Kwa'"),
    ('nucl1465', u'Nuclear Ma\u2019ya', u"Nuclear Ma'ya"),
    ('nucl1476', u'Nuclear \u2019Are\u2019are', u"Nuclear 'Are'are"),
    ('nucl1564', u'Nuclear Ida\u2019an', u"Nuclear Ida'an"),
    ('nucl1684', u'Nuclear Ga\u2019anda', u"Nuclear Ga'anda"),
]


def upgrade():
    params = {'type': 'name', 'description': 'Glottolog', 'lang': 'en'}
    
    update_name = sa.text('UPDATE language SET updated = now(), '
        'name = :after WHERE id = :id AND name = :before')

    del_lang_ident = sa.text('DELETE FROM languageidentifier AS li '
        'WHERE language_pk = (SELECT pk FROM language WHERE id = :id) '
        'AND EXISTS (SELECT 1 FROM identifier WHERE pk = li.identifier_pk '
        'AND name = :before AND type = :type AND description = :description '
        'AND lang = :lang)').bindparams(**params)

    del_ident = sa.text('DELETE FROM identifier AS i WHERE name = :before '
        'AND type = :type AND description = :description AND lang = :lang '
        'AND NOT EXISTS (SELECT 1 FROM languageidentifier WHERE identifier_pk = i.pk)'
        ).bindparams(**params)

    insert_ident = sa.text('INSERT INTO identifier '
        '(created, updated, active, version, type, description, lang, name) '
        'SELECT now(), now(), true, 1, :type, :description, :lang, :name '
        'WHERE NOT EXISTS (SELECT 1 FROM identifier WHERE type = :type '
        'AND description = :description AND lang = :lang AND name = :name)'
        ).bindparams(**params)

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
        ).bindparams(**params)

    for id, before, after in GCODE_OLD_NEW:
        op.execute(update_name.bindparams(id=id, before=before, after=after))
        op.execute(del_lang_ident.bindparams(id=id, before=before))
        op.execute(del_ident.bindparams(before=before))
        op.execute(insert_ident.bindparams(name=after))
        op.execute(insert_lang_ident.bindparams(id=id, name=after))


def downgrade():
    pass
