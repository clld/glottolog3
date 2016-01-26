# coding=utf-8
"""unattached dialects

Revision ID: 21f6064e20a6
Revises: 4d2e5b8ecc09
Create Date: 2016-01-21 17:00:39.138936

"""

# revision identifiers, used by Alembic.
revision = '21f6064e20a6'
down_revision = '4d2e5b8ecc09'

import datetime
import re

from alembic import op
import sqlalchemy as sa


MAP_PATTERN = re.compile('\[(?P<gc>[a-z0-9]{8})\][^\[]+\[(?P<hid>[a-z0-9]+)\]')

# update father_pk, family_pk
# The below should be filed as dialects as per the below (same format, to
# mean that [glottocode] is a dialect of [iso]). (I'll weed out any
# dialect-level duplicates in the dialect overhaul step).
reparent = sa.text("""\
  UPDATE languoid
  SET father_pk = father.pk, family_pk = father.family_pk
  FROM (
    SELECT pk, family_pk
    FROM languoid WHERE hid = :hid)
  AS father
  WHERE languoid.pk IN (SELECT pk FROM language WHERE id = :gc)""")

REPARENT = """\
High East Prussian [high1271] Saxon-Low [nds]
South Guelderish [sout2637] Dutch [nld]
Öcher [oche1235] K\"olsch [ksh]
Leonese [leon1250] Asturian [ast]
Kentish [kent1253] Old English (ca. 450-1100) [ang]
Acadian [acad1238] French [fra]
Gallo [gall1275] French [fra]
Alsatian [alsa1241] German [deu]
Algherese [algh1238] Catalan [cat]
Aluku [aluk1239] Aukan [djk]
Bologna Emiliano [bolo1260] Emiliano [egl]
Canary Islands Spanish [cana1258] Spanish [spa]
Central Emiliano [cent1959] Emiliano [egl]
Eastern Emiliano [east2275] Emiliano [egl]
Faliscan [fali1263] Faliscan [xfa]
Franco-Ontarien [fran1263] French [fra]
Maltese English [malt1247] English [eng]
New Zealand English [newz1240] English [eng]
Western Emiliano [west2342] Emiliano [egl]
Fiorentino [fior1235] Italian [ita]
Nonstandard Central Catalan [nons1235] Catalan [cat]
Paramaccan [para1317] Aukan [djk]
Matawai [mata1310] Saramaccan [srm]
Eastphalian [east2289] Saxon-Low [nds]
Hessian [hess1238] Saxon-Upper [sxu]
Lunigiano [luni1238] Emiliano [egl]
Mantovano [mant1264] Lombardo [lmo]
Saramaccan [sara1339] Saramaccan [srm]
Nuorese [nuor1238] Logudorese Sardinian [src]
Pugliese [pugl1238] Napoletano-Calabrese [nap]
Sammarinese [samm1243] Romagnol [rgn]
Southern Romagnolo [sout2611] Romagnol [rgn]
Northern Romagnolo [nort2607] Romagnol [rgn]
Thuringian [thur1252] Saxon-Upper [sxu]
Vogherese-Pavese [vogh1238] Emiliano [egl]
Angevin [ange1244] French [fra]
Berrichon [berr1239] French [fra]
Bourbonnais [bour1246] French [fra]
Bourguignon [bour1247] French [fra]
Lorraine [lorr1242] French [fra]
Lorrain Franconian [lorr1243] Luxembourgeois [ltz]
British Creole [brit1243] Jamaican Creole [jam]
Jerriais [jerr1238] French [fra]
Dgernesiais [dger1238] French [fra]
Mahanji [maha1296] Kinga [zga]
Molisano [moli1245] Napoletano-Calabrese [nap]
Norman [norm1245] French [fra]
Poitevin [poit1240] French [fra]
Québécois [queb1247] French [fra]
Santongeais [sant1407] French [fra]
Brabants [brab1243] Dutch [nld]
Schleswig-Holstein Low German [schl1236] Saxon-Low [nds]
Low Alemannic [lowa1241] German-Swiss [gsw]
Franche-Comtois [fran1262] Arpitan [frp]"""

# active = False, father_pk = null
# add row in superseded, relation='duplicate'
# The below nodes are actually duplicates of existing entities which
# already have (SIL- and) glottcodes as per the below (format is "name
# [glottocode] name [iso]" to indicate that [glottocode] is identical to the
# (glottocode which is equivalent to) [iso]) . They are thus spurious and
# should be retired/bookeeped or whatever our current scheme is:
deactivate = sa.text("UPDATE language SET active = FALSE WHERE id = :gc")
decouple = sa.text("""\
UPDATE languoid SET father_pk = NULL
WHERE pk IN (SELECT pk FROM language WHERE id = :gc)""")
supersede = sa.text("""\
INSERT INTO superseded (created, updated, active, languoid_pk, replacement_pk, relation)
SELECT now(), now(), TRUE, l.pk, ll.pk, 'duplicate'
FROM languoid AS ll, language AS l
WHERE l.id = :gc AND (ll.hid = :hid OR ll.pk IN (SELECT pk FROM language WHERE id = :hid))""")

DUPLICATES = """\
Corso-Sardinian [cors1240] [sard1256]
Franc-Comtois [fran1261] Franche-Comtois [fran1262]
Upper Silesian German [uppe1399] Silesian [sli]
Afro-Seminole Creole [afro1253] Afro-Seminole Creole [afs]
Bajan [baja1264] Bajan [bjs]
Belizean Creole [beli1259] Belize Kriol English [bzj]
Dalmatian [dalm1242] Dalmatian [dlm]
Grenadian Creole English [gren1246] Grenadian Creole English [gcl]
Tobagonian Creole English [toba1281] Tobagonian Creole English [tgh]
Trinidadian Creole English [trin1275] Trinidadian Creole English [trf]
Turks and Caicos Creole English [turk1309] Turks And Caicos Creole English [tch]
Vincentian Creole English [vinc1242] Vincentian Creole English [svc]
Krio [krio1247] Krio [kri]
Limburgish (Macro-Dutch) [limb1264] Limburgish [lim]
Nicaraguan Creole English [nica1251] Nicaragua Creole English [bzk]
Sranan [sran1239] Sranan [srn]"""


def upgrade():
    conn = op.get_bind()
    for line in REPARENT.splitlines():
        conn.execute(reparent, **MAP_PATTERN.search(line).groupdict())

    for line in DUPLICATES.splitlines():
        match = MAP_PATTERN.search(line)
        conn.execute(deactivate, gc=match.group('gc'))
        conn.execute(decouple, gc=match.group('gc'))
        conn.execute(supersede, **match.groupdict())


def downgrade():
    pass
