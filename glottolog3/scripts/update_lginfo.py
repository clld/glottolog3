# coding=utf-8
"""
Updating the language-country relationships
-------------------------------------------

We only add new relationships for languages which so far have not been related to any
country. This is to make sure the relationships determined by algorithms other than
Harald's remain stable.

input:
- glottolog-data/languoids/lginfo.csv
- glottolog-data/languoids/forkel_countries.tab
- glottolog-data/languoids/forkel_family_justifications-utf8.tab
- glottolog-data/languoids/forkel_subclassification_justifications-utf8.tab

output:
- should we append changes to glottolog-data/languoids/changes.json?
"""
from __future__ import unicode_literals
import re

import transaction
from sqlalchemy import true

from clld.lib import dsv
from clld.db.meta import DBSession
from clld.db.models.common import (
    Language, Contribution, ValueSet, Value, Parameter, ValueSetReference, Source,
)

from glottolog3.models import (
    Languoid, Country, Macroarea, LanguoidLevel, TreeClosureTable,
)
from glottolog3.lib.util import get_map
from glottolog3.scripts.util import (
    update_relationship, WORD_PATTERN, get_args, get_bib, get_bibkeys,
)

REF_PATTERN = re.compile('\*\*(?P<id>\d+)\*\*(?::(?P<pages>[\divx\-, ]+))?')


def get_lginfo(args, filter=None):
    return [
        (r.id, r) for r in
        dsv.reader(
            args.data_dir.joinpath('languoids', 'lginfo.csv'),
            delimiter=',',
            namedtuples=True)
        if filter is None or filter(r)]


def countries(args, languages):
    """update relations between languages and countries they are spoken in.
    """
    cname_map = {
        'Tanzania': 'Tanzania, United Republic of',
        'Russia': 'Russian Federation',
        'South Korea': 'Korea, Republic of',
        'Iran': 'Iran, Islamic Republic of',
        'Syria': 'Syrian Arab Republic',
        'Laos': "Lao People's Democratic Republic",
        r"C\^ote d'Ivoire": "Côte d'Ivoire",
        'British Virgin Islands': 'Virgin Islands, British',
        'Bolivia': 'Bolivia, Plurinational State of',
        'Venezuela': 'Venezuela, Bolivarian Republic of',
        'Democratic Republic of the Congo': 'Congo, The Democratic Republic of the',
        'Micronesia': 'Micronesia, Federated States of',
    }
    count = 0
    countries = {}
    for row in dsv.reader(
            args.data_dir.joinpath('languoids', 'forkel_countries.tab'), encoding='latin1'):
        hid, cnames = row[0], row[1:]
        if hid not in languages:
            languages[hid] = Languoid.get(hid, key='hid', default=None)
        if not languages[hid]:
            args.log.warn('unknown hid in countries.tab: %s' % hid)
            continue
        l = languages[hid]
        if l.countries:
            # we only add country relations to new languages or languages which have none.
            continue
        for cname in set(cnames):
            if cname not in countries:
                q = cname if '(' not in cname else cname.split('(')[0].strip()
                countries[cname] = Country.get(cname_map.get(q, q), key='name', default=None)
            if not countries[cname]:
                args.log.warn('unknown country name in countries.tab: %s' % cname)
                continue
            c = countries[cname]
            if c.id not in [_c.id for _c in l.countries]:
                l.countries.append(c)
                count += 1

    args.log.info('countries: %s relations added' % count)


def macroareas(args, languages):
    ma_map = get_map(Macroarea)

    # we store references to languages to make computation of cumulated macroareas for
    # families easier
    lang_map = {}
    for hid, info in get_lginfo(args, lambda x: x.macro_area):
        if hid not in languages:
            languages[hid] = Languoid.get(hid, key='hid', default=None)
        if not languages[hid]:
            continue
        lang_map[languages[hid].pk] = languages[hid]
        update_relationship(
            languages[hid].macroareas, [ma_map[info.macro_area]], log=args.log)

    for family in DBSession.query(Languoid)\
            .filter(Languoid.level == LanguoidLevel.family)\
            .filter(Language.active == true()):
        mas = []
        for lang in DBSession.query(TreeClosureTable.child_pk)\
                .filter(TreeClosureTable.parent_pk == family.pk):
            if lang[0] in lang_map:
                mas.extend(lang_map[lang[0]].macroareas)
        update_relationship(family.macroareas, mas, log=args.log)
    args.log.info('macroareas done')


def coordinates(args, languages):
    diff = lambda x, y: abs(x - y) > 0.001

    for hid, info in get_lginfo(args, lambda x: x.longitude and x.latitude):
        if hid not in languages:
            languages[hid] = Languoid.get(hid, key='hid', default=None)
        if not languages[hid]:
            continue
        language = languages[hid]
        lat, lon = map(float, [info.latitude, info.longitude])

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
    hh_bibkey_to_glottolog_id = {}
    for rec in get_bib(args):
        for provider, bibkeys in get_bibkeys(rec).items():
            if provider == 'hh':
                for bibkey in bibkeys:
                    hh_bibkey_to_glottolog_id[bibkey] = rec['glottolog_ref_id']
                break

    def substitute_hh_bibkeys(m):
        return '**%s**' % hh_bibkey_to_glottolog_id[m.group('bibkey')]

    #
    # create mappings to look up glottolog languoids matching names in justification files
    #
    langs_by_hid = languages
    langs_by_hname = {}
    langs_by_name = {}

    # order by active to make sure, we active languoid overwrite the data of obsolete ones.
    for l in DBSession.query(Languoid).order_by(Languoid.active):
        langs_by_hname[l.jsondata.get('hname')] = l
        langs_by_hid[l.hid] = l
        langs_by_name[l.name] = l

    def normalize_pages(s):
        return (s or '').strip().rstrip(',') or None

    for id_, type_ in [('fc', 'family'), ('sc', 'subclassification')]:
        for i, row in enumerate(dsv.reader(
                args.data_dir.joinpath('languoids', 'forkel_%s_justifications-utf8.tab' % type_))):
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
            if comment:
                comment = re.sub('\*\*(?P<bibkey>[^\*]+)\*\*', substitute_hh_bibkeys, comment)

            #
            # TODO: look for [NOCODE_ppp] patterns as well!?
            #

            refs = [(int(m.group('id')), normalize_pages(m.group('pages')))
                    for m in REF_PATTERN.finditer(
                    re.sub('\*\*(?P<bibkey>[^\*]+)\*\*', substitute_hh_bibkeys, row[2]))]

            vs = None
            for _vs in l.valuesets:
                if _vs.parameter.id == id_:
                    vs = _vs
                    break

            if not vs:
                args.log.info('%s %s ++' % (l.id, type_))
                vs = ValueSet(
                    id='%s%s' % (id_, l.pk),
                    description=comment,
                    language=l,
                    parameter=Parameter.get(id_),
                    contribution=Contribution.first())
                DBSession.add(Value(
                    id='%s%s' % (id_, l.pk),
                    name='%s - %s' % (l.level, l.status),
                    valueset=vs))
                DBSession.flush()
            else:
                if vs.description != comment:
                    args.log.info('%s %s ~~ description: %s ---> %s' % (l.id, type_, vs.description, comment))
                    vs.description = comment

            for r in vs.references:
                DBSession.delete(r)

            for r, pages in refs:
                    vs.references.append(ValueSetReference(
                        source=Source.get(str(r)),
                        description=pages))

        args.log.info('%s %s' % (i, type_))


def main(args):
    with transaction.manager:
        languages = {}
        justifications(args, languages)
        countries(args, languages)
        macroareas(args, languages)
        coordinates(args, languages)


if __name__ == '__main__':
    main(get_args())
