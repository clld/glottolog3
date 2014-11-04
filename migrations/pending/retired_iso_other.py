# coding=utf-8
"""retired iso other

Revision ID: 
Revises: 
Create Date: 

"""

# revision identifiers, used by Alembic.

revision = ''
down_revision = ''

import datetime
import json

from alembic import op
import sqlalchemy as sa

from glottolog3.lib.util import glottocode

JSON_KEY = 'iso_retirement'


def upgrade():
    conn = op.get_bind()

    check_invariant = sa.text('SELECT l.pk, array_agg(i.name) '
        'FROM language AS l JOIN languoid as ll ON l.pk = ll.pk '
        'JOIN languageidentifier AS li ON li.language_pk = l.pk '
        'JOIN identifier AS i ON li.identifier_pk = i.pk AND i.type = :type '
        'GROUP BY l.pk HAVING count(*) > 1 ORDER BY l.pk', conn).bindparams(type='iso639-3')

    select_lang = sa.text('SELECT l.pk AS l_pk, li.pk AS li_pk, i.pk AS i_pk, i.name AS iso '
        'FROM language AS l JOIN languoid as ll ON l.pk = ll.pk '
        'LEFT JOIN (languageidentifier AS li JOIN identifier AS i '
        'ON li.identifier_pk = i.pk AND i.type = :type) ON li.language_pk = l.pk '
        'WHERE l.id = :id', conn).bindparams(type='iso639-3')

    del_lang_ident = sa.text('DELETE FROM languageidentifier WHERE pk = :pk', conn)
    del_ident = sa.text('DELETE FROM identifier WHERE pk = :pk', conn)

    insert_ident = sa.text('INSERT INTO identifier '
        '(created, updated, active, version, name, type, lang) '
        'VALUES (now(), now(), true, 1, :name, :type, :lang) '
        'RETURNING (pk)', conn).bindparams(type='iso639-3', lang='en')
    insert_lang_ident = sa.text('INSERT INTO languageidentifier '
        '(created, updated, active, version, language_pk, identifier_pk) '
        'VALUES (now(), now(), true, 1, :language_pk, :identifier_pk)', conn)

    update_hid = sa.text('UPDATE languoid AS l SET hid = :after '
        'WHERE hid = :before AND pk = :pk', conn)

    def set_iso(id, after, set_hid=False):
        l_pk, li_pk, i_pk, before = select_lang.execute(id=id).first()
        if before != after:
            if before is not None:
                del_lang_ident.execute(pk=li_pk)
                del_ident.execute(pk=i_pk)
            if after is not None:
                i_pk = insert_ident.scalar(name=after)
                insert_lang_ident.execute(language_pk=l_pk, identifier_pk=i_pk)
            if set_hid:
                update_hid.execute(pk=l_pk, before=before, after=after)

    select_json = sa.text('SELECT jsondata FROM language WHERE id = :id', conn)
    update_json = sa.text('UPDATE language SET updated = now(), jsondata = :jsondata '
        'WHERE id = :id', conn)

    def retirement(id, dct):
        jsondata = json.loads(select_json.scalar(id=id))
        del dct['id']
        jsondata[JSON_KEY] = dct
        update_json.execute(id=id, jsondata=json.dumps(jsondata))

    other = {o['iso']: o for o in OTHER}
    codes = {}

    assert check_invariant.execute().first() is None

    # move split agp from para1306 to subfamily para1320 and assign prf to the former
    retirement('para1320', other['agp'])
    set_iso('para1306', 'prf')
    set_iso('para1320', 'agp')

    # add ubl and lbl for splitted dialects
    retirement('alba1269', other['bhk'])
    set_iso('buhi1243', 'ubl')
    set_iso('libo1242', 'lbl')

    # rename merged with drl
    retirement('band1337', other['bjd'])

    # rename merged with kml
    retirement('uppe1424', other['kgh'])

    # add xpq and xnt for splitted dialects
    retirement('mohe1244', other['mof'])

    # assign mol to dialect
    retirement('mold1248', other['mol'])
    set_iso('mold1248', 'mol')

    # add new muw as split source
    #gc = glottocode(other['muw']['name'], conn, codes)
    #retirement(gc, other['muw'])
    #set_iso(gc, 'muw')

    # rename split language nru to Narua
    retirement('naxi1245', other['nbf'])
    set_iso('yong1270', None)

    # missing remedy
    retirement('piru1241', other['ppr'])

    # make puz retired instead of pub
    retirement('puru1262', other['puz'])

    # assign wre to languoid
    retirement('ware1252', other['wre'])
    set_iso('ware1252', 'wre')

    # add yug as replacement
    retirement('yugh1239', other['yuu'])

    assert check_invariant.execute().first() is None

    raise NotImplementedError


def downgrade():
    pass


OTHER = [  # 12
    {'id': u'para1306', 'iso': 'agp', 'name': u'Paranan',
     'cr': u'2009-086', 'effective': '2010-01-18', 'reason': 'split',
     'remedy': 'Split into Pahanan Agta [apf] and Paranan [prf] (new identifier)',
     'comment': u'\u201cThis is a case where although there is a high level of intelligibility between the two groups, this can be explained by the historical origins of the two groups. In isolated Palanan town, there was almost nobody for the Paranan non-Negritos and the Pahanan Negritos to talk to except each other, and they interacted for trade and other purposes, to the point that the language of the non-Negritos converged lexically (but not so much so grammatically) with the language of the Negritos. Lexicostatistical percentages are skewed by this convergence, and are completely incapable of representing the fact that the underlying stratum of the languages are different, indicating that one does not originate from the other and so one should not be considered a dialect of the other. The underlying substrata are a perfect match for the objectively-observable racial differences between the Pahanan Agta speakers (who are Black Filipinos, a.k.a. "Negritos") and the Paranan speakers (who are not "Negritos"). Despite their obvious convergence due to isolation of these two groups in the same area for centuries or longer, differences still remain that reveal the separate origins of the two groups and their respective languages, and the language of the Pahanan Agta in some ways remains closer to the languages of other neighboring Black Filipino groups (e.g. the Dupaningan Agta and the Casiguran Agta) than it does to the Paranan language. Besides the clear differences in the underlying substrata, the clearly distinct ethnolinguistic identities and the lack of a common body of literature or mutually- recognized standard reinforce the separate listing of these two languages.\u201d'},
    {'id': u'alba1269', 'iso': 'bhk', 'name': u'Albay Bicolano',
     'cr': u'2009-078', 'effective': '2010-01-18', 'reason': 'split',
     'remedy': "Split into Buhi'non Bikol [ubl]; Libon Bikol [lbl]; Miraya Bikol [rbl]; West Albay Bikol [fbl]",
     'comment': u'\u201cThe currently-existing "Bicolano, Albay" does not correspond to any of the accepted Bikol subgroupings, the most widely-recognized of which is McFarland (1974) which was also adopted by Zorc (1977). Jason Lobel, the supporter of this request, has also done extensive research on the languages of the Bikol region, and his findings largely support those of McFarland (1974) and likewise do not support a "Bicolano Albay" language that would include Buhi\'non, Miraya, and Bikol Libon. Such a language is also not supported by the identities of the people of Albay province themselves. Therefore, it is requested that the "Bicolano Albay" entry be split into four entries, "Bikol West Albay", "Bikol Miraya", "Bikol, Libon", and "Bikol Buhi\'non". (Note also that calling any of these languages "Bicolano" or "Bikolano" is a mistake because "Bikolano" is the name of the ethnic group while "Bikol" is the name of the languages.)\u201d'},
    {'id': u'band1337', 'iso': 'bjd', 'name': u'Bandjigali',
     'cr': u'2011-145', 'effective': '2012-02-03', 'reason': 'merge',
     'remedy': u'Merged into [drl] Darling and renamed Paakantyi',
     'comment': u'\u201cIn addition to this change in primary name, there is also evidence that Paakantyi should be merged with Bandjigali (bjd), which Ethnologue classifies as a separate language (Bowern 2011b; AUSTLANG 2011).\nWafer and Lisserrague state that "Hercus has demonstrated in detail (1980, 1982, 1989, 1993, 1994) that the various distinct but closely related language varieties in this group... are dialects of a single language. She divides the "Darling River (Paakantyi) Language Group" into the \'northern dialects\' and the \'southern dialects\'" (2008: 264).\nBandjigali (bjd) is considered by Bowern (2011b), AUSTLANG, and Wafer and Lisserague (2008: 263, 276) to be one of many dialects of Paakanti and it should be merged with Paakantyi. Wafer and Lisserague follow Hercus 1993 in how she groups the dialects:\nPaakantyi: language\n1.) Northern Paakantyi (Northern Darling River): Dialect Group (2008: 263) - Paaruntyi: Dialect (2008: 268)\n- Kurnu: Dialect (2008: 269)\n- Nhaawuparlku: Dialect (2008: 270)\n- Milpulo: Dialect (2008: 271)\n2.) Southern Paakantyi (Southern Darling River): Dialect Group (2008: 263) - Wilyaali: Dialect (2008: 272)\n- Thangkaali: Dialect (2008: 273)\n- Pulaali: Dialect (2008: 274)\n- Wanyuparlku: Dialect (2008: 275)\n- Pantyikali: (Ethnologue\'s Bandjigali, bjd) Dialect (2008: 276)\n- Marrawarra: Dialect (2008: 277)\n- Southern Paakantyi (Proper): Dialect (2008: 278)\n- Parrintyi: Dialect (2008: 279)\nPaakantyi is still considered to be the sole member of a subgroup variously called Paakantyi by Bowern (2010a) and AUSTLANG (2011) and Darling River Group by Lissarrague and Wafer (2008: 263). This subgroup is part of the Pama-Nyungan family.\u201d'},
    {'id': u'uppe1424', 'iso': 'kgh', 'name': u'Upper Tanudan Kalinga',
     'cr': u'2011-079', 'effective': '2012-02-03', 'reason': 'merge',
     'remedy': u'merged with Lower Tanudan Kalinga [kml] and named Tanudan Kalinga',
     'comment': u'Since there is deemed no basic language communication differences between Upper and Lower Tanudan, in regards to the Kalinga language, the proposal is to reflect that lack of difference in merging the two into simply Tanudan. This proposal is associated with the Change Request for the retirement of the Upper Tanudan language code.'},
    {'id': u'mohe1244', 'iso': 'mof', 'name': u'Mohegan-Montauk-Narragansett',
     'cr': u'2009-013', 'effective': '2010-01-18', 'reason': 'split',
     'remedy': 'split into Mohegan-Pequot [xpq] and Narragansett [xnt]',
     'comment': u'\u201cThe situation of the languages of eastern southern New England in the 17 and 18 centuries is a little confusing... Given the certainty that Narragansett does not belong with Mohegan-Pequot and the uncertainty of whether or not it belongs with Massachusett, it seems a prudent idea to give Narragansett its own place within ISO 639-3.\u201d'},
    {'id': None, 'iso': 'mol', 'name': u'Moldavian',
     'cr': None, 'effective': '2008-11-03', 'reason': 'merge',
     'remedy': u'Merge with Romanian [ron] (same as [rum] 639-2/B)',
     'comment': u'Moldavian was merged into Romanian [ISO 639-3 ron].'},
    {'id': None, 'iso': 'muw', 'name': u'Mundari',
     'cr': u'2007-065', 'effective': '2008-02-18', 'reason': 'split',
     'remedy': 'Split into Munda [unx] and Mundari [unr] (new identifier)',
     'comment': u'Munda is regarded as a separate language from Mundari by numerous published sources. Munda and Mundari are enumerated separately on the national census, thus indicating a separate ethnolinguisic identity.'},
    {'id': u'naxi1245', 'iso': 'nbf', 'name': u'Naxi',
     'cr': u'2010-023', 'effective': '2011-05-18', 'reason': 'split',
     'remedy': 'split into Naxi [nxq] and Narua [nru]',
     'comment': u'Based on first-hand experience by SIL researchers, Naxi (Naxi Proper) and Narua (Mosuo) are almost completely unintelligible with previously unexposed speakers only being able to understand isolated words of the other\'s speech.\nBoth languages are considered "dialects" of the same language (called Naxi) by most Chinese linguists, and most speakers are included in the official nationality group called Naxi, though Sichuan province speakers of Narua are classed within the Mongolian nationality. However, in Chinese linguistics it is common to call closely related languages whose speakers share the same nationality classification "dialects" of the same language even when mutual intelligibility is very low or non-existent. The separate identities of the Naxi and the Na/Mosuo peoples are well-known and documented in Chinese anthropological circles. There is no common literature or orthography in use between the Naxi and Narua speakers.'},
    {'id': u'piru1241', 'iso': 'ppr', 'name': u'Piru',
     'cr': u'2012-096', 'effective': '2013-01-23', 'reason': None,
     'remedy': None,
     'comment': u"In the previous cycle, the languages Piru and Luhu were combined, as the Piru group were determined to be a dialect of Luhu. The forms were written so that the code and name retained were [ppr] Piru. The name for this combined group should be Luhu.\nThe old information is most likely based on Taguchi's lexicostatistic data. However, Collins has done more in depth research in the area and has published a few articles that show\nthe similirities. The following are some excerpts from the published sources in the sources section of this request: \u201cAt the head of Piru Bay, a very small number of elderly in Piru village still remember the indigenous language. Although Dyen (1978:392) was doubtful about the classification of this speech community, it can be demonstrated that Piru is a dialect of Luhu, a fact which Van Hoevell correctly stated in 1877. For a variety of historical and social reasons (outlined in Collins 1983b), the language of Piru has undergone a number of irregular changes and now it is close to extinction. The most striking differences between Luhu and Piru are the loss of almost all productive verbal conjugations in the latter dialect and the sporadic influence of East Piru Bay languages and, perhaps, Alune. This is especially apparent in the numerous loan words which have slipped into Piru, apparently\nvia Eti, a Kaibobo-speaking village a few kilometers southward on the east shore of the bay. A few unexpected sound correspondences may also be attributed to Eti.\u201d (Collins1982)\n\u201cAs noted 20 years ago (Collins 1983), Piru is closely related to the language of Luhu. Moreover, Sachse (1919:44) considered Piru and Luhu the two dialects of \u2018Behasa Loehoe\u2019. In fact, Piru probably represents the northernmost point in the chain of Luhu-speaking villages that spread across the whole Hoamoal peninsula before 1650 (footnote 19 - Payapo\u2019s map (1980:62-3) suggests just this kind of isolation of Piru, with non-Luhu- speaking villages, such as Ariate and Talaga, intervening between the main Luhu-speaking areas to the south and Piru, which Payapo also labeled as Luhu-speaking.) When De Valming\u2019s forced resettlement policy depopulated the peninsula, the links in that chain were broken, leaving Piru speakers isolated from Luhu speakers, especially those remaining in Luhu itself...The borrowing of vocabulary, especially from Eti, a village which traditionally spoke and East Piru Bay language related to Kaibobo, but also lexical items from nearby Alune speaking villages, has made Piru diverge from contemporary Luhu. However, the relationship of Piru with Luhu is striking, (footnote 20 \u2013 Taguchi (1989:49) apparently did\nnot understand the argumentation inf Collins (1983:79-81). In those pages, Piru and Luhu are considered variants (dialects) of the same Luhu language because they share phonological innovations, not because there is a tradition that Hoamoal formed a single language. His untested assertion that these two \u2018speech forms are probably not mutually intelligable\u2019 is unlikely to be true. His informant, aged only 45 might, might perhaps experience difficulty, but speakers of Luhu would find Piru (if it was ever spoken in public) easy to understand. With no data from either of the Luhu or Piru wordlists used by Taguchi, it is difficult to understand where he sees the problem in intelligibility. Note that Payapo (1980), a speaker of Luhu, considered Piru a variant of Luhu. The reader can refer to the brief comparative wordlist, based on Collins(1977-79), found in Appendix 1 here to form his or her own opinion about the extent of differences between Piru and Luhu.) even to the point of both variants displaying mundai \u2018man, male\u2019 and sima \u2018who\u2019, found in no other\nWest Piru Bay languages \u2013 except Batumerah, as noted above.\u201d (Collins 2003)"},
    {'id': u'puru1262', 'iso': 'puz', 'name': u'Purum Naga',
     'cr': u'2013-008', 'effective': '2014-02-03', 'reason': 'merge',
     'remedy': u'merged into Purum [pub]',
     'comment': u'Both the languages [puz] and [pub] have the same information on location and Population in most available resources. So it seems to be one language.'},
    {'id': None, 'iso': 'wre', 'name': u'Ware',
     'cr': u'2007-024', 'effective': '2008-01-14', 'reason': 'non-existent',
     'remedy': None,
     'comment': u'Neither we, the SIL-UTB survey team, nor any other people we have spoken to have heard of the Ware people. Since no information is given in the current Ethnologue entry as to the location of the Ware it is difficult to say conclusively that they do not exist, but the genetic classification of E.10 suggest that they would be located in the north of Tanzania.\nIn July 2005 and January/February 2006 the UTB survey team was in Mara Region, Tanzania where many of the languages in the E.10 group to which Ware is said to belong are located, and found no knowledge of the Ware. An SIL language team located in Arusha Region also failed to discover any knowledge of the Ware amongst the people in their area.\nSince there seems to be no knowledge of the Ware in northern Tanzania now, we would recommend retiring this language code element.'},
    {'id': u'yugh1239', 'iso': 'yuu', 'name': u'Yugh',
     'cr': u'2013-031', 'effective': '2014-02-03', 'reason': 'duplicate',
     'remedy': u'Yugh [yuu] is a duplicate of Yug [yug]',
     'comment': u'[yuu] Yugh (Yug) and [yug] Yug (Sym-Ket) are the same language.\nI suggest retiring code [yuu] because [yug] is easier to remember, but if [yuu] is older it might be better to retain it instead. The fact that Ethnologue has an entry for [yuu] but not for [yug] might be reason to retain [yuu], though perhaps they could move their article to [yug].\nIn order to complete the change request, the form \u201cRequest for New Language Code Element in ISO 639-3\u201d (file name \u201cISO639-3_NewCodeRequestForm.doc\u201d or \u201cISO639- 3_NewCodeRequestForm.rtf\u201d) must also be submitted for each new identifier that is to be created. That step can be deferred until this form has been processed by the ISO 639-3 registrar, provided that sufficient information on the rationale is given in (b) above.\nIn the case of a minority language that has been considered in some contexts to be a dialect of a major language, yet is divergent enough to be unintelligible to speakers of the standard variety of the major language, it may be more beneficial for the users of the ISO 639-3 and 639-2 code sets to create a new code element for the divergent language variety without splitting the existing code element of the major language. The ISO 639-3 Registration Authority may make this determination when considering a request involving a major language and a highly distinct \u201cdialect.\u201d If such a course is followed, the rationale for the decision will be published in a comment by the Registration Authority on approval of the requested addition for the divergent variety.'}
]
