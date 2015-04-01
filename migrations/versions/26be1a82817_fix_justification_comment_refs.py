# coding=utf-8
"""fix justification comment refs

Revision ID: 26be1a82817
Revises: 264eb9832040
Create Date: 2015-04-01 11:37:58.114000

"""

# revision identifiers, used by Alembic.
revision = '26be1a82817'
down_revision = '264eb9832040'

import datetime

from alembic import op
import sqlalchemy as sa

ID_BEFORE_AFTER = [
    ('fc104990',
         u'Convincing published lexical evidence exist for the relatedness of Northern-Southern Je in a Je subgroup **85851**, '
         u'Je-Jabuti **105441**, Je-Karaja **306521**:268-287, Je-Rikbaktsa **76034**, Ofaye **62158**, Maxakalian-Je **48053**, '
         u'**111963**, Je-Aimore **80559**. For Kamakanan and Puri-Coropo-Coroado the lexical parallels adduced by **158410** and '
         u'**153186** remain to be corroborated using Kamakanan proto-forms **79381** and Puri-Coropo-Coroado proto-forms **21917**. '
         u'For Kariri, Bororoan and Chiquitano there is suggestive, but not conclusive grammatical evidence **306521**:265 **63035** '
         u'**73916** (also shared by Carib and Tupi **75120**) and little in the way of lexicon. For Fulni\xf4, Guat\xf3 and Ot\xed '
         u'there is insufficient evidence whatsoever **306521**:262-287.',
         u'Convincing published lexical evidence exist for the relatedness of Northern-Southern Je in a Je subgroup **85851**, '
         u'Je-Jabuti **105441**, Je-Karaja **306521**:268-287, Je-Rikbaktsa **76034**, Ofaye **54471**, Maxakalian-Je **48053**, '
         u'**111963**, Je-Aimore **80559**. For Kamakanan and Puri-Coropo-Coroado the lexical parallels adduced by **158410** and '
         u'**153186** remain to be corroborated using Kamakanan proto-forms **79381** and Puri-Coropo-Coroado proto-forms **21917**. '
         u'For Kariri, Bororoan and Chiquitano there is suggestive, but not conclusive grammatical evidence **306521**:265 **63035** '
         u'**73916** (also shared by Carib and Tupi **75120**) and little in the way of lexicon. For Fulni\xf4, Guat\xf3 and Ot\xed '
         u'there is insufficient evidence whatsoever **306521**:262-287.'),
    ('sc24537', '**132826**:i-xiii', '**31549**:i-xiii'),
]


def upgrade():
    update_comment = sa.text('UPDATE valueset SET updated = now(), '
        'description = :after WHERE id = :id AND description = :before')
    for id, before, after in ID_BEFORE_AFTER:
        op.execute(update_comment.bindparams(id=id, before=before, after=after))


def downgrade():
    pass
