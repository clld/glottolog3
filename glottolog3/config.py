# -*- coding: utf-8 -*-
from clld.lib.bibtex import Record
from clld.util import slug


CFG = {
    'EXPORTS': [],
    'PUBLICATIONS': [
        Record(
            'ARTICLE', 'HammarstroemEtAl2011Oslo',
            ('author', u'Harald Hammarström and Sebastian Nordhoff'),
            ('year', '2011'),
            ('title', 'LangDoc: Bibliographic Infrastructure for Linguistic Typology'),
            ('journal', 'Oslo Studies in Language'),
            ('volume', '3'),
            ('number', '2'),
            ('pages', '31-43'),
            ('url', 'https://www.journals.uio.no/index.php/osla/article/view/75/199'),
        ),
        Record(
            'UNPUBLISHED', 'HammarstroemEtAl2011Howmany',
            ('author', u"Hammarström, Harald and Nordhoff, Sebastian"),
            ('year', u"2011"),
            ('title', u"How many languages have so far been described?"),
            ('howpublished', u"Paper presented at NWO Endangered Languages Programme Conference, Leiden, April 2011"),
        ),
        Record(
            'UNPUBLISHED', 'NordhoffEtAl2011ALT',
            ('author', u"Sebastian Nordhoff and Harald Hammarström"),
            ('year', u"2011"),
            ('title', u"Countering bibliographical bias with LangDoc, a bibliographical database for lesser-known languages"),
            ('howpublished', u"Paper presented at the Association for Linguistic Typology 9th Biennial Conference, July, Hong Kong"),
        ),
        Record(
            'INPROCEEDINGS', 'NordhoffEtAl2011iswc',
            ('author', u"Sebastian Nordhoff and Harald Hammarström"),
            ('year', u"2011"),
            ('title', u"Glottolog/Langdoc: Defining dialects, languages, and language families as collections of resources"),
            ('volume', u"783"),
            ('series', u"CEUR Workshop Proceedings"),
            ('booktitle', u"Proceedings of the First International Workshop on Linked Science 2011"),
            ('url', u"http://iswc2011.semanticweb.org/fileadmin/iswc/Papers/Workshops/LISC/nordhoff.pdf"),
        ),
        Record(
            'INCOLLECTION', 'ldl-glottolog',
            ('author', u"Sebastian Nordhoff"),
            ('year', u"2012"),
            ('title', u"Linked Data for linguistic diversity research: Glottolog/Langdoc and ASJP"),
            ('crossref', u"ldl2012"),
            ('pages', u"191-200"),
            ('editor', u"Chiarcos, Christian and Nordhoff, Sebastian and Hellmann, Sebastian"),
            ('booktitle', u"Linked Data in Linguistics. Representing and Connecting Language Data and Language Metadata"),
            ('publisher', u"Springer"),
            ('address', u"Heidelberg"),
            ('ISBN', u"978-3-642-28248-5"),
            ('DOI', u"10.1007/978-3-642-28249-2"),
            ('url', u"http://www.springer.com/computer/ai/book/978-3-642-28248-5"),
        ),
        Record(
            'INCOLLECTION', 'ldl-llod',
            ('author', u"Christian Chiarcos and Sebastian Hellmann and Sebastian Nordhoff"),
            ('year', u"2012"),
            ('title', u"Linking linguistic resources: Examples from the Open Linguistics Working Group"),
            ('crossref', "ldl2012"),
            ('pages', u"201-216"),
            ('editor', u"Chiarcos, Christian and Nordhoff, Sebastian and Hellmann, Sebastian"),
            ('booktitle', u"Linked Data in Linguistics. Representing and Connecting Language Data and Language Metadata"),
            ('publisher', u"Springer"),
            ('address', u"Heidelberg"),
            ('ISBN', u"978-3-642-28248-5"),
            ('DOI', u"10.1007/978-3-642-28249-2"),
            ('url', u"http://www.springer.com/computer/ai/book/978-3-642-28248-5"),
        ),
        Record(
            'ARTICLE', 'ChiarcosEtAl2012tal',
            ('author', u"Christian Chiarcos and Sebastian Hellmann and Sebastian Nordhoff"),
            ('year', u"2012"),
            ('title', u"Towards a Linguistic Linked Open Data cloud: The Open Linguistics Working Group"),
            ('journal', u"Traitement Automatique des Langues")),
        Record(
            'INPROCEEDINGS', 'NordhoffEtAl2012lrec',
            ('author', u"Sebastian Nordhoff and Harald Hammarström"),
            ('year', u"2012"),
            ('title', u"Glottolog/Langdoc: Increasing the visibility of grey literature for low-density languages"),
            ('booktitle', "Proceedings of LREC 2012"),
        ),
        Record(
            'UNPUBLISHED', 'NordhoffEtAl2012DH',
            ('author', u"Sebastian Nordhoff and Harald Hammarström"),
            ('year', u"2012"),
            ('title', u"Cataloguing linguistic diversity: Glottolog/Langdoc"),
            ('note', u"Proceedings of Digital Humanities 2012, July, Hamburg"),
        ),
    ],
    'PARTNERSITES': [
        {
            'name': 'Ethnologue',
            'href': lambda l: "http://www.ethnologue.com/show_language.asp?code="
            + l.get_code('ISO'),
            'condition': lambda l: l.get_code('ISO'),
            'logo': "ethnologue.png",
            'rdf': "owl:sameAs",
        },
        {
            'name': 'SIL',
            'href': lambda l: "http://www.sil.org/iso639-3/documentation.asp?id="
            + l.get_code('ISO'),
            'condition': lambda l: l.get_code('ISO'),
            'logo': "sil.gif",
            'rdf': "owl:sameAs",
        },
        {
            'name': 'Lexvo',
            'href': lambda l: "http://lexvo.org/id/iso639-3/" + l.get_code('ISO'),
            'condition': lambda l: l.get_code('ISO'),
            'logo': "lexvo.gif",
            'rdf': "owl:sameAs",
        },
        {
            'name': 'Wikipedia',
            'href': lambda l: "http://en.wikipedia.org/wiki/ISO_639:"
            + l.get_code('ISO'),
            'condition': lambda l: l.get_code('ISO'),
            'rdf': "owl:sameAs",
            'logo': "wikipedia.png"
        },
        {
            'name': 'OLAC',
            'href': lambda l: "http://www.language-archives.org/language/"
            + l.get_code('ISO'),
            'condition': lambda l: l.get_code('ISO'),
            'rdf': "rdfs:seeAlso",
            'logo': "olac.png"
        },
        {
            'name': 'Multitree',
            'href': lambda l: "http://multitree.org/codes/"
            + l.get_code('ISO'),
            'condition': lambda l: l.get_code('ISO'),
            'rdf': "owl:sameAs",
            'logo': "multitree.png"
        },
        {
            'name': 'MultitreePrivate',
            'href': lambda l: "http://multitree.linguistlist.org/codes/"
            + l.get_code('multitree'),
            'condition': lambda l: l.get_code('multitree'),
            'rdf': "rdfs:seeAlso",
            'logo': "multitree.png"
        },
        {
            'name': 'LL-Map',
            'href': lambda l: "http://www.llmap.org/maps/by-code/%s.html"
            % l.get_code('ISO'),
            'condition': lambda l: l.get_code('ISO'),
            'rdf': "rdfs:seeAlso",
            'logo': "LL-logo.png"
        },
        {
            'name': 'LinguistList',
            'href':
            lambda l: "http://linguistlist.org/forms/langs/LLDescription.cfm?code="
            + l.get_code('ISO'),
            'condition': lambda l: l.get_code('ISO'),
            'rdf': "rdfs:seeAlso",
            'logo': "LL-logo.png"
        },
        {
            'name': 'Odin',
            'href': lambda l: "http://odin.linguistlist.org/igt_urls.php?lang="
            + l.get_code('ISO'),
            'condition': lambda l: l.get_code('ISO'),
            'rdf': "rdfs:seeAlso",
            'logo': "odin.png"
        },
        {
            'name': 'WALS',
            'href': lambda l: "http://wals.info/languoid/lect/wals_code_"
            + l.get_code('WALS'),
            'condition': lambda l: l.get_code('WALS'),
            'rdf': "owl:sameAs",
            'logo': "wals.png"
        },
        {
            'name': 'WALSgenus',
            'href': lambda l: "http://wals.info/languoid/genus/"
            + slug(l.get_code('WALSgenus')),
            'condition': lambda l: l.get_code('WALSgenus'),
            'rdf': "owl:sameAs",
            'logo': "wals.png"
        },
        {
            'name': 'WALSfamily',
            'href': lambda l: "http://wals.info/languoid/family/"
            + slug(l.get_code('WALSfamily')),
            'condition': lambda l: l.get_code('WALSfamily'),
            'rdf': "owl:sameAs",
            'logo': "wals.png"
        },
        {
            'name': 'Endangered Languages',
            'href': lambda l: "http://www.endangeredlanguages.com/lang/"
            + l.get_code('ISO'),
            'rdf': "rdfs:seeAlso",
            'condition': lambda l: l.get_code('ISO'),
        },
        #{
        #    'name': 'Unesco',
        #'href': "http://www.unesco.org/culture/languages-atlas/en/atlasmap/language-id-",
        #    'linkcode': "unescoid",
        #    'linkpostcode': "html",
        #    'condition': "unescoid",
        #    'logo': "unesco.png"
        #},
        #{
        #{
        #    'name': 'musico',
        #    'href': "",
        #    'linkcode': "musico",
        #    'linkpostcode': "",
        #    'condition': "musico",
        #    'logo': "musico.png"
        #},
        #{
        #    'name': 'languagelandscapes',
        #    'href': "",
        #    'linkcode': "languagelandscapes",
        #    'linkpostcode': "",
        #    'condition': "languagelandscapes",
        #    'logo': "languagelandscapes.png"
        #},
        #{
        #    'name': 'wolp',
        #    'href': "",
        #    'linkcode': "wolp",
        #    'linkpostcode': "",
        #    'condition': "wolp",
        #    'logo': "wolp.ico"
        #},
        #{
        #    'name': 'scriptsource',
        #    'href': "http://scriptsource.org/lang/",
        #    'linkcode': "iso",
        #    'linkpostcode': "",
        #    'condition': "iso",
        #    'logo': "scriptsource.png"
        #}
    ],
}
