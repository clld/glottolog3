from clld.lib.bibtex import Record

PUBLICATIONS = [
    Record(
        'ARTICLE', 'swj-glottocodes',
        ('author', 'Harald Hammarström and Robert Forkel'),
        ('title', 'Glottocodes: Identifiers Linking Families, Languages and Dialects to Comprehensive Reference Information'),
        ('year', '2021'),
        ('journal', 'Semantic Web Journal'),
        ('url', 'http://www.semantic-web-journal.net/system/files/swj2843.pdf'),
    ),
    'hh:hel:Hammarstrom:Visualization',
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
    'sn:HammarstroemEtAl2011Oslo',
    'sn:HammarstroemEtAl2011Howmany',
    Record(
        'UNPUBLISHED', 'NordhoffEtAl2011ALT',
        ('author', u"Sebastian Nordhoff and Harald Hammarström"),
        ('year', u"2011"),
        ('title',
         u"Countering bibliographical bias with LangDoc, a bibliographical database for lesser-known languages"),
        ('howpublished',
         u"Paper presented at the Association for Linguistic Typology 9th Biennial Conference, July, Hong Kong"),
    ),
    'sn:NordhoffEtAl2011iswc',
]


def github(path):
    """
    :param path: relative (to the root) path of a file in the glottolog data repository
    :return: URL to a file in Glottolog's data repository on GitHub
    """
    return 'https://github.com/glottolog/glottolog/blob/master/{0}'.format(path)


class ISOSite(object):
    """
    Subclass this virtual base class to register a new site that can be linked to using ISO codes.
    """
    img = None
    name = None

    def url(self, iso):
        raise NotImplementedError()  # pragma: no cover

    def href_label_img_alt(self, iso):
        name = self.name or self.__class__.__name__
        return self.url(iso), '[{0}] at {1}'.format(iso, name), self.img, name


class ISO(ISOSite):
    img = 'sil.gif'
    name = 'ISO 639-3'

    def url(self, iso):
        return "https://iso639-3.sil.org/code/" + iso


class OLAC(ISOSite):
    img = 'olac.png'

    def url(self, iso):
        return "http://www.language-archives.org/language/" + iso


class Odin(ISOSite):
    img = 'odin.png'

    def url(self, iso):
        return "http://odin.linguistlist.org/igt_urls.php?lang=" + iso


class PartnerSite(object):
    """
    Subclass this virtual base class to register a new site which we have links to in languoid INI
    files.
    """
    domain = None
    img = None

    def match(self, domain):
        return domain == self.domain

    @property
    def name(self):
        return self.__class__.__name__.replace('_', ' ')

    def href_label_img_alt(self, link):
        label = '{0} at {1}'.format(link['label'], self.name) if link['label'] else self.name
        return link['url'], label, self.img, self.name


class PHOIBLE(PartnerSite):
    domain = 'phoible.org'
    img = 'phoible.png'


class WALS(PartnerSite):
    domain = 'wals.info'
    img = 'wals.png'


class APiCS(PartnerSite):
    domain = 'apics-online.info'
    img = 'apics.png'


class Endangered_Languages_Project(PartnerSite):
    domain = 'endangeredlanguages.com'
    img = 'ELP.png'


class Wikipedia(PartnerSite):
    domain = 'en.wikipedia.org'
    img = 'wikipedia.png'


class Wikidata(PartnerSite):
    domain = 'www.wikidata.org'
    img = 'wikidata.png'


class AIATSIS(PartnerSite):
    domain = 'collection.aiatsis.gov.au'
    img = 'aiatsis.png'
