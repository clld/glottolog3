# coding=utf-8
"""fix uniqueness violations in family names

Revision ID: 95efeef62d
Revises: 3cd6bf1141c8
Create Date: 2013-12-05 11:04:04.060573

"""

# revision identifiers, used by Alembic.
revision = '95efeef62d'
down_revision = '3cd6bf1141c8'

import datetime

from alembic import op
import sqlalchemy as sa


NAMES = {
    "bina1276": "Greater Binanderean",
    "moro1282": "Baka-Beli",
    "mond1268": "Nuclear Mondzish",
    "kowa1246": "Unclassified Madang",
    "oira1260": "Eastern Mongolic",
    "nort2871": "Sangil-Sangir",
    "nucl1701": "Oromoid",
    "yukp1242": "Opon-Yukpan",
    "tang1354": "Ataitan",
    "jehh1244": "Kayong-Jeh-Halang",
    "etul1244": "Akweya",
    "muni1256": "Munan",
    "tami1294": "Tamil-Irula",
    "sout2849": "Tobaic",
    "port1292": "Orkon-Port Vato-Dakaka",
    "west2647": "Maijiki-Siona",
    "anga1291": "Sau-Angal-Kewa",
    "duka1247": "Northwestern Kainji",
    "kela1257": "Dayic",
    "hatu1244": "Saparuan",
    "dida1244": "Neyo-Dida",
    "bugi1243": "Tamanic-Bugis",
    "cham1327": "Aceh-Chamic",
    "coat1242": "Coatlan-Loxicha Zapotec",
    "obol1242": "Lower Cross",
}


def upgrade():
    conn = op.get_bind()
    for id, name in NAMES.items():
        conn.execute("update language set name = %s where id = %s", (name, id))


def downgrade():
    pass

