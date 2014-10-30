# coding=utf-8
"""fix identifier other

Revision ID: 2a0e1708e80
Revises: 209d7444dee3
Create Date: 2014-10-30 10:59:24.592000

"""

# revision identifiers, used by Alembic.

revision = '2a0e1708e80'
down_revision = '209d7444dee3'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()

    del_ident = sa.text('DELETE FROM identifier '
        'WHERE type = :type AND name = ANY(:delete)', conn)

    del_langident = sa.text('DELETE FROM languageidentifier AS li '
        'WHERE EXISTS (SELECT 1 FROM identifier '
            'WHERE type = :type AND name = ANY(:delete) '
            'AND pk = li.identifier_pk)', conn)

    del_langident.execute(type='name', delete=DELETE)
    del_ident.execute(type='name', delete=DELETE)

    del_orphaned = sa.text('DELETE FROM identifier AS i '
        'WHERE NOT EXISTS (SELECT 1 FROM languageidentifier '
            'WHERE identifier_pk = i.pk)', conn)

    del_orphaned.execute()


def downgrade():
    pass


DELETE =[
    u'"etc."',

    u'10.0',
    u'11.0',
    u'12.0',
    u'1st division',
    u'2 varieties: Aymara (Central)/Aymara (Southern)',
    u'2.0',
    u'2.2.1 Bwamu',
    u'2.2.10 Tusy\xe3',
    u'2.2.4 Gan-doghosye-padorho-komono',
    u'2.2.5 Kirma-tyurama',
    u'2.2.6 Wara-natioro',
    u'2.2.7 Kulango',
    u'2nd division',
    u'3 varieties: Kadazan (Coastal)/...',
    u'3.0',
    u'5 varieties: Tamang (Eastern)/...',
    u'5. Katla group',
    u'82% with Northern Slavey.',
    u'9.0',

    u'Hourrites#Langue',
    u'Jenisseische Sprachen#Das Ketische',
    u'Luo#Langue',
    u'Malaiische und indonesische Sprache#Geschichte',
    u'Praprusoj#Kristanigo kaj la praprusa lingvo',
    u'Urartu#Langue et \xe9criture',

    u'82% with Northern Slavey.',
    u'less than 60% with Nakama.',
    u'Lexical similarity 65% with Nuk',
    u'The Detah-Ndilo dialect developed from intermarriage between the Yellowknife subdivision of the Chipewyan and the Dogrib. Lexical similarity 84% with Southern Slavey',

    u'Bardimaya Baadeemaia Badimaia Badimala Badimara Bardimaia Barimaia Bidungu Padimaia Padinaia Parimaia Patimara Patimay Waadal Wardal Badi-maia Wallawe Yamadgee Yamaji',
    u'but Chuksang understand Tangbe. They are reported to understand Gurung but Gurung speakers do not understand Seke.',
    u'Eastern and Western Gurung do not have adequate intelligibility to handle complex and abstract discourse. Daduwa town seems central linguistically.',
    u'Kyrgyzstan, Ukraine, USA, Iran, Azerbaijan, Georgia, Tajikistan, Turkmenistan, Uzbekistan, Armenia, Kazakhstan, Russia, Turkey',
    u'Related to Gurung. Some similarities with Thakali and Manangba. Very different from Lowa. Tangbe people do not understand Chuksang very well',
    u'The Detah-Ndilo dialect developed from intermarriage between the Yellowknife subdivision of the Chipewyan and the Dogrib. Lexical similarity 84% with Southern Slavey',
    u'USA, India, Oman, Philippines, Singapore, United Kingdom, Pakistan',
]
