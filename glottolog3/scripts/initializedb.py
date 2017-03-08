# coding: utf8
from __future__ import unicode_literals, division
import sys
from collections import defaultdict
from time import time

from clld.scripts.util import initializedb, Data
from clld.db.meta import DBSession
from clld.db.models import common
from clld.db import fts
from clldutils.jsonlib import load
from clldutils.text import split_text

from pyglottolog.api import Glottolog
from pyglottolog.references import BibFile
from pyglottolog import objects

from glottolog3 import models
from glottolog3.scripts.util import recreate_treeclosure, compute_pages
from glottolog3.scripts.loadutil import load_languoid, load_ref


def main(args):
    fts.index('fts_index', models.Ref.fts, DBSession.bind)
    DBSession.execute("CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA public;")

    dataset = common.Dataset(
        id='glottolog',
        name="Glottolog 3.0",
        publisher_name="Max Planck Institute for the Science of Human History",
        publisher_place="Jena",
        publisher_url="https://shh.mpg.de",
        license="http://creativecommons.org/licenses/by/4.0/",
        domain='glottolog.org',
        contact='glottolog@shh.mpg.de',
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'})

    data = Data()
    for i, (id_, name) in enumerate([
        ('hammarstroem', 'Harald Hammarström'),
        ('haspelmath', 'Martin Haspelmath'),
        ('forkel', 'Robert Forkel')
    ]):
        ed = data.add(common.Contributor, id_, id=id_, name=name)
        common.Editor(dataset=dataset, contributor=ed, ord=i + 1)
    DBSession.add(dataset)

    clf = data.add(common.Contribution, 'clf', id='clf', name='Classification')
    DBSession.add(common.ContributionContributor(
        contribution=clf, contributor=data['Contributor']['hammarstroem']))

    for pid, pname in [
        ('fc', 'Family classification'),
        ('sc', 'Subclassification'),
        ('vitality', 'Degree of endangerment'),
    ]:
        data.add(common.Parameter, pid, id=pid, name=pname)

    legacy = load(args.data_file('glottocode2version.json'))
    for gc, version in legacy.items():
        data.add(models.LegacyCode, gc, id=gc, version=version)

    glottolog = Glottolog()
    for ma in objects.Macroarea:
        data.add(models.Macroarea, ma.name, id=ma.name, name=ma.value, description=ma.description)

    for country in glottolog.countries:
        data.add(models.Country, country.id, id=country.id, name=country.name)

    lgcodes, mas, countries, lgsources = {}, {}, {}, defaultdict(list)
    languoids = list(glottolog.languoids())
    nodemap = {l.id: l for l in languoids}
    for lang in languoids:
        for ref in lang.sources:
            lgsources['{0.provider}#{0.bibkey}'.format(ref)].append(lang.id)
        load_languoid(data, lang, nodemap)
        mas[lang.id] = [ma.name for ma in lang.macroareas]
        countries[lang.id] = [c.id for c in lang.countries]
        lgcodes[lang.id] = lang.id
        if lang.hid:
            lgcodes[lang.hid] = lang.id
        if lang.iso:
            lgcodes[lang.iso] = lang.id

    for gc in glottolog.glottocodes:
        if gc not in data['Languoid'] and gc not in legacy:
            common.Config.add_replacement(gc, None, model=common.Language)

    for obj in load(glottolog.references_path('replacements.json')):
        common.Config.add_replacement(
            '{0}'.format(obj['id']),
            '{0}'.format(obj['replacement']) if obj['replacement'] else None,
            model=common.Source)

    DBSession.flush()
    for lid, maids in mas.items():
        for ma in maids:
            DBSession.add(models.Languoidmacroarea(
                languoid_pk=data['Languoid'][lid].pk,
                macroarea_pk=data['Macroarea'][ma].pk))

    for lid, cids in countries.items():
        for cid in cids:
            DBSession.add(models.Languoidcountry(
                languoid_pk=data['Languoid'][lid].pk,
                country_pk=data['Country'][cid].pk))

    for doctype in glottolog.hhtypes:
        data.add(
            models.Doctype, doctype.id, id=doctype.id,
            name=doctype.name,
            abbr=doctype.abbv,
            ord=doctype.rank)

    for bib in glottolog.bibfiles:
        data.add(
            models.Provider,
            bib.id,
            id=bib.id,
            name=bib.title,
            description=bib.description,
            abbr=bib.abbr,
            url=bib.url)
    DBSession.flush()

    s = time()
    for i, entry in enumerate(
            BibFile(glottolog.build_path('monster-utf8.bib')).iterentries()):
        #if i > 50000:
        #    break
        if i % 10000 == 0:
            print('{0}: {1:.3}'.format(i, time() - s))
            s = time()
        ref = load_ref(data, entry, lgcodes, lgsources)
        if 'macro_area' in entry.fields:
            for ma in split_text(entry.fields['macro_area'], separators=',;', strip=True):
                ma = 'North America' if ma == 'Middle America' else ma
                ma = objects.Macroarea.get('Papunesia' if ma == 'Papua' else ma)
                DBSession.add(models.Refmacroarea(
                    ref_pk=ref.pk, macroarea_pk=data['Macroarea'][ma.name].pk))


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
    recreate_treeclosure()
    for row in list(DBSession.execute(
        "select pk, pages, pages_int, startpage_int from source where pages_int < 0")):
        pk, pages, number, start = row
        _start, _end, _number = compute_pages(pages)
        if _number > 0 and _number != number:
            DBSession.execute(
                "update source set pages_int = %s, startpage_int = %s where pk = %s" %
                (_number, _start, pk))
            DBSession.execute(
                "update ref set endpage_int = %s where pk = %s" %
                (_end, pk))

    known = set(load(args.data_file('glottocode2version.json')).keys())
    for lang in DBSession.query(common.Language):
        if lang.id not in known:
            lang.update_jsondata(new=True)


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
