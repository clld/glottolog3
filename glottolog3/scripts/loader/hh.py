"""
Updating the language-country relationships
-------------------------------------------

We only add new relationships for languages which so far have not been related to any
country. This is to make sure the relationships determined by algorithms other than
Harald's remain stable.
"""
from clld.lib import dsv
from clld.db.meta import DBSession
from clld.db.models.common import (
    Language, Contribution, ValueSet, Value, Parameter, ValueSetReference, Source,
)

from glottolog3.models import (
    Languoid, Country, Macroarea, LanguoidLevel, TreeClosureTable,
)
from glottolog3.lib.util import get_map, REF_PATTERN
from glottolog3.scripts.util import update_relationship, PAGES_PATTERN, WORD_PATTERN


def countries(args, languages):
    count = 0
    countries = {}
    for row in dsv.reader(args.data_file('countries.tab'), encoding='latin1'):
        hid, cnames = row[0], row[1:]
        if hid not in languages:
            languages[hid] = Languoid.get(hid, key='hid', default=None)
        if not languages[hid]:
            continue
        l = languages[hid]
        if l.countries:
            continue
        for cname in set(cnames):
            if cname not in countries:
                countries[cname] = Country.get(cname, key='name', default=None)
            if not countries[cname]:
                continue
            c = countries[cname]
            if c.id not in [_c.id for _c in l.countries]:
                l.countries.append(c)
                count += 1

    print 'countries:', count, 'relations added'


def macroareas(args, languages):
    ma_map = get_map(Macroarea)

    # we store references to languages to make computation of cumulated macroareas for
    # families easier
    lang_map = {}

    for hid, macroarea in dsv.reader(args.data_file('macroareas.tab')):
        if hid not in languages:
            languages[hid] = Languoid.get(hid, key='hid', default=None)
        if not languages[hid]:
            continue
        lang_map[languages[hid].pk] = languages[hid]
        update_relationship(languages[hid].macroareas, [ma_map[macroarea]], log=args.log)

    for family in DBSession.query(Languoid)\
            .filter(Languoid.level == LanguoidLevel.family)\
            .filter(Language.active == True):
        mas = []
        for lang in DBSession.query(TreeClosureTable.child_pk)\
                .filter(TreeClosureTable.parent_pk == family.pk):
            if lang[0] in lang_map:
                mas.extend(lang_map[lang[0]].macroareas)
        update_relationship(family.macroareas, mas, log=args.log)
    print 'macroareas done'


def coordinates(args, languages):
    diff = lambda x, y: abs(x - y) > 0.001

    for hid, lon, lat in dsv.reader(args.data_file('coordinates.tab')):
        if hid not in languages:
            languages[hid] = Languoid.get(hid, key='hid', default=None)
        if not languages[hid]:
            continue
        language = languages[hid]
        lat, lon = map(float, [lat, lon])

        if not language.latitude or not language.longitude:
            language.longitude, language.latitude = lon, lat
            args.log.info('++ %s' % language.id)
        elif diff(language.longitude, lon) or diff(language.latitude, lat):
            language.longitude, language.latitude = lon, lat
            args.log.info('~~ %s' % language.id)


def justifications(args, languages):
    """
    - text goes into ValueSet.description
    - refs go into ValueSetReference objects
    """
    def normalized_pages(s):
        if PAGES_PATTERN.match(s or ''):
            return s or ''

    #
    # create mappings to look up glottolog languoids matching names in justification files
    #
    langs_by_hid = languages
    langs_by_hname = {}
    langs_by_name = {}

    for l in DBSession.query(Languoid).filter(Languoid.active == False):
        langs_by_hname[l.jsondatadict.get('hname')] = l
        langs_by_hid[l.hid] = l
        langs_by_name[l.name] = l

    for l in DBSession.query(Languoid).filter(Languoid.active == True):
        langs_by_hname[l.jsondatadict.get('hname')] = l
        langs_by_hid[l.hid] = l
        langs_by_name[l.name] = l

    for id_, type_ in [('fc', 'family'), ('sc', 'subclassification')]:
        for i, row in enumerate(dsv.reader(args.data_file('%s_justifications.tab' % type_))):
            name = row[0]
            name = name.replace('_', ' ') if not name.startswith('NOCODE') else name
            l = langs_by_hname.get(name, langs_by_hid.get(name, langs_by_name.get(name)))
            if not l:
                args.log.warn('ignoring %s' % name)
                continue

            _r = 3 if type_ == 'family' else 2
            comment = (row[_r].strip() or None) if len(row) > _r else None
            if comment and not WORD_PATTERN.search(comment):
                comment = None

            #
            # TODO: look for [NOCODE_ppp] patterns as well!?
            #

            refs = [(int(m.group('id')), normalized_pages(m.group('comment')))
                    for m in REF_PATTERN.finditer(row[2])]

            vs = None
            for _vs in l.valuesets:
                if _vs.parameter.id == id_:
                    vs = _vs
                    break

            if not vs:
                args.log.info('%s %s ++' % (l.id, type_))
                vs = ValueSet(
                    id='%s%s' % (type_, l.id),
                    description=comment,
                    language=l,
                    parameter=Parameter.get(id_),
                    contribution=Contribution.first())
                DBSession.add(Value(
                    id='%s%s' % (type_, l.id),
                    name='%s - %s' % (l.level, l.status),
                    valueset=vs))
                DBSession.flush()
            else:
                if vs.description != comment:
                    args.log.info('%s %s ~~ description' % (l.id, type_))
                    vs.description = comment

            for r in vs.references:
                DBSession.delete(r)

            for r, pages in refs:
                    vs.references.append(ValueSetReference(
                        source=Source.get(str(r)),
                        description=pages))

        args.log.info('%s %s' % (i, type_))


def update(args):
    languages = {}
    justifications(args, languages)
    countries(args, languages)
    macroareas(args, languages)
    coordinates(args, languages)
