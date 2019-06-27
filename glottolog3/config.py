from clld.lib.bibtex import Record

PUBLICATIONS = [
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
        ('title',
         u"Countering bibliographical bias with LangDoc, a bibliographical database for lesser-known languages"),
        ('howpublished',
         u"Paper presented at the Association for Linguistic Typology 9th Biennial Conference, July, Hong Kong"),
    ),
    Record(
        'INPROCEEDINGS', 'NordhoffEtAl2011iswc',
        ('author', u"Sebastian Nordhoff and Harald Hammarström"),
        ('year', u"2011"),
        (
        'title', u"Glottolog/Langdoc: Defining dialects, languages, and language families as collections of resources"),
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


class WALS(PartnerSite):
    domain = 'wals.info'
    img = 'wals.png'


class APiCS(PartnerSite):
    domain = 'apics-online.info'
    img = 'apics.png'


class Endangered_Laguages(PartnerSite):
    domain = 'endangeredlanguages.com'
    img = 'ELP.png'
