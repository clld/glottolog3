# coding: utf8
from __future__ import unicode_literals, division
from collections import defaultdict
from time import time
import re

from clld.scripts.util import Data, add_language_codes
from clld.db.meta import DBSession
from clld.db.models import common
from clld.db import fts
from clld.lib.bibtex import EntryType
from clldutils import jsonlib
from clldutils.text import split_text
from clldutils.misc import slug

from pyglottolog.references import BibFile
from pyglottolog.languoids import Macroarea

from glottolog3 import models
from glottolog3.scripts.util import recreate_treeclosure, compute_pages

PREF_YEAR_PATTERN = re.compile('\[(?P<year>(1|2)[0-9]{3})(\-[0-9]+)?\]')
YEAR_PATTERN = re.compile('(?P<year>(1|2)[0-9]{3})')


def gc2version(args):
    return args.pkg_dir.parent / 'archive' / 'glottocode2version.json'


def load(args):
    fts.index('fts_index', models.Ref.fts, DBSession.bind)
    DBSession.execute("CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA public;")

    dataset = common.Dataset(
        id='glottolog',
        name="Glottolog {0}".format(args.args[0]),
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
        ('bank', 'Sebastian Bank'),
        ('forkel', 'Robert Forkel'),
        ('haspelmath', 'Martin Haspelmath'),
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

    legacy = jsonlib.load(gc2version(args))
    for gc, version in legacy.items():
        data.add(models.LegacyCode, gc, id=gc, version=version)

    glottolog = args.repos
    for ma in Macroarea:
        data.add(
            models.Macroarea,
            ma.name,
            id=ma.name,
            name=ma.value,
            description=ma.description)

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

    for obj in jsonlib.load(glottolog.references_path('replacements.json')):
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
            description=doctype.description,
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
        if i % 10000 == 0:
            args.log.info('{0}: {1:.3}'.format(i, time() - s))
            s = time()
        ref = load_ref(data, entry, lgcodes, lgsources)
        if 'macro_area' in entry.fields:
            for ma in split_text(entry.fields['macro_area'], separators=',;', strip=True):
                ma = 'North America' if ma == 'Middle America' else ma
                ma = Macroarea.get('Papunesia' if ma == 'Papua' else ma)
                DBSession.add(models.Refmacroarea(
                    ref_pk=ref.pk, macroarea_pk=data['Macroarea'][ma.name].pk))


def prime(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
    recreate_treeclosure()

    for lpk, mas in DBSession.execute("""\
select
  l.pk, array_agg(distinct lma.macroarea_pk)
from
  language as l,
  treeclosuretable as t,
  languoidmacroarea as lma,
  macroarea as ma
where
  l.pk = t.parent_pk and
  t.child_pk = lma.languoid_pk and
  lma.macroarea_pk = ma.pk and
  l.pk not in (select languoid_pk from languoidmacroarea)
group by l.pk"""):
        for mapk in mas:
            DBSession.add(models.Languoidmacroarea(languoid_pk=lpk, macroarea_pk=mapk))

    for row in list(DBSession.execute(
        "select pk, pages, pages_int, startpage_int from source where pages_int < 0"
    )):
        pk, pages, number, start = row
        _start, _end, _number = compute_pages(pages)
        if _number > 0 and _number != number:
            DBSession.execute(
                "update source set pages_int = %s, startpage_int = %s where pk = %s" %
                (_number, _start, pk))
            DBSession.execute(
                "update ref set endpage_int = %s where pk = %s" %
                (_end, pk))

    with jsonlib.update(gc2version(args), indent=4) as legacy:
        for lang in DBSession.query(common.Language):
            if lang.id not in legacy:
                lang.update_jsondata(new=True)
                legacy[lang.id] = args.args[0]

    def items(s):
        if not s:
            return set()
        r = []
        for ss in set(s.strip().split()):
            if '**:' in ss:
                ss = ss.split('**:')[0] + '**'
            if ss.endswith(','):
                ss = ss[:-1].strip()
            r.append(ss)
        return set(r)

    refs = {
        r[0]: r[1]
        for r in DBSession.query(models.Refprovider.id, models.Refprovider.ref_pk)}
    valuesets = {
        r[0]: r[1] for r in DBSession.query(common.ValueSet.id, common.ValueSet.pk)}

    for lang in args.repos.languoids():
        clf = lang.classification_comment
        if clf:
            if clf.subrefs:
                if items(lang.cfg['classification']['subrefs']) != \
                        items(lang.cfg['classification'].get('sub')):
                    vspk = valuesets.get('sc-{0}'.format(lang.id))
                    for ref in clf.subrefs:
                        spk = refs.get(ref.key)
                        DBSession.add(
                            common.ValueSetReference(source_pk=spk, valueset_pk=vspk))


def add_identifier(languoid, data, name, type, description, lang='en'):
    if len(lang) > 3:
        # Weird stuff introduced via hhbib_lgcode names. Roll back language parsing.
        name, lang = '{0} [{1}]'.format(name, lang), 'en'
    identifier = data['Identifier'].get((name, type, description, lang))
    if not identifier:
        identifier = data.add(
            common.Identifier,
            (name, type, description, lang),
            id='{0}-{1}-{2}-{3}'.format(
                slug(name), slug(type), slug(description or ''), lang),
            name=name,
            type=type,
            description=description,
            lang=lang)
    DBSession.add(common.LanguageIdentifier(language=languoid, identifier=identifier))


def load_languoid(data, lang, nodemap):
    dblang = data.add(
        models.Languoid,
        lang.id,
        id=lang.id,
        hid=lang.hid,
        name=lang.name,
        bookkeeping=lang.category == models.BOOKKEEPING,
        newick=lang.newick_node(nodemap).newick,
        latitude=lang.latitude,
        longitude=lang.longitude,
        status=models.LanguoidStatus.get(
            lang.endangerment.name if lang.endangerment else 'safe'),
        level=models.LanguoidLevel.from_string(lang.level.name),
        father=data['Languoid'][lang.lineage[-1][1]] if lang.lineage else None)
    if lang.iso:
        add_language_codes(data, dblang, lang.iso)

    for prov, names in lang.names.items():
        for name in names:
            l = 'en'
            if '[' in name and name.endswith(']'):
                name, l = [s.strip() for s in name[:-1].split('[', 1)]
            add_identifier(dblang, data, name, 'name', prov, lang=l)

    for prov, ids in lang.identifier.items():
        for id_ in split_text(ids, separators=',;'):
            add_identifier(dblang, data, id_, prov, None)

    clf = lang.classification_comment
    if clf:
        for attr, pid in [('sub', 'sc'), ('family', 'fc')]:
            if not getattr(clf, attr):
                continue
            vs = common.ValueSet(
                id='%s-%s' % (pid, lang.id),
                description=getattr(clf, attr),
                language=dblang,
                parameter=data['Parameter'][pid],
                contribution=data['Contribution']['clf'])
            DBSession.add(common.Value(id='%s-%s' % (pid, lang.id), valueset=vs))

    iso_ret = lang.iso_retirement
    if iso_ret:
        DBSession.add(models.ISORetirement(
            id=iso_ret.code,
            name=iso_ret.name,
            description=iso_ret.comment,
            effective=iso_ret.effective,
            reason=iso_ret.reason,
            remedy=iso_ret.remedy,
            change_request=iso_ret.change_request,
            languoid=dblang))

    eth_cmt = lang.ethnologue_comment
    if eth_cmt:
        DBSession.add(models.EthnologueComment(
            comment=eth_cmt.comment,
            code=eth_cmt.isohid,
            type=eth_cmt.comment_type,
            affected=eth_cmt.ethnologue_versions,
            languoid=dblang))


def load_ref(data, entry, lgcodes, lgsources):
    kw = {'jsondata': {}, 'language_note': entry.fields.get('lgcode')}
    for col in common.Source.__table__.columns:
        if col.name in entry.fields:
            kw[col.name] = entry.fields.get(col.name)
    for col in models.Ref.__table__.columns:
        if col.name in entry.fields:
            kw[col.name] = entry.fields.get(col.name)
    for col in entry.fields:
        if col not in kw:
            kw['jsondata'][col] = entry.fields[col]
    try:
        btype = EntryType.from_string(entry.type.lower())
    except ValueError:
        btype = EntryType.misc

    # try to extract numeric year, startpage, endpage, numberofpages, ...
    if kw.get('year'):
        # prefer years in brackets over the first 4-digit number.
        match = PREF_YEAR_PATTERN.search(kw.get('year'))
        if match:
            kw['year_int'] = int(match.group('year'))
        else:
            match = YEAR_PATTERN.search(kw.get('year'))
            if match:
                kw['year_int'] = int(match.group('year'))
    if kw.get('publisher'):
        p = kw.get('publisher')
        if ':' in p:
            address, publisher = [s.strip() for s in kw['publisher'].split(':', 1)]
            if 'address' not in kw or kw['address'] == address:
                kw['address'], kw['publisher'] = address, publisher

    if kw.get('numberofpages'):
        try:
            kw['pages_int'] = int(kw.get('numberofpages').strip())
        except ValueError:
            pass

    if kw.get('pages'):
        start, end, number = compute_pages(kw['pages'])
        if start is not None:
            kw['startpage_int'] = start
        if end is not None:
            kw['endpage_int'] = end
        if number is not None and 'pages_int' not in kw:
            kw['pages_int'] = number

    kw.update(
        id=entry.fields['glottolog_ref_id'],
        fts=fts.tsvector(
            '\n'.join(v for k, v in entry.fields.items() if k != 'abstract')),
        name='%s %s' % (
            entry.fields.get('author', 'na'), entry.fields.get('year', 'nd')),
        description=entry.fields.get('title') or entry.fields.get('booktitle'),
        bibtex_type=btype)
    ref = models.Ref(**kw)
    DBSession.add(ref)
    DBSession.flush()

    reflangs = []
    no_ca = [{'degruyter'}, {'benjamins'}]
    provs = set()
    for key in entry.fields['srctrickle'].split(','):
        key = key.strip()
        if key:
            if key in lgsources:
                reflangs.extend(lgsources[key])
            prov, key = key.split('#', 1)
            provs.add(prov)
            DBSession.add(models.Refprovider(
                provider_pk=data['Provider'][prov].pk,
                ref_pk=ref.pk,
                id='{0}:{1}'.format(prov, key)))

    langs, trigger = entry.languoids(lgcodes)
    if trigger and ((provs in no_ca) or (reflangs)):
        # Discard computerized assigned languoids for bibs where this does not make sense,
        # or for bib entries that have been manually assigned in a Languoid's ini file.
        langs, trigger = [], None

    for lid in set(reflangs + langs):
        DBSession.add(
            common.LanguageSource(language_pk=data['Languoid'][lid].pk, source_pk=ref.pk))
    if trigger:
        ref.ca_language_trigger = trigger

    doctypes, trigger = entry.doctypes(data['Doctype'])
    if trigger is None or provs not in no_ca:
        for dt in set(doctypes):
            DBSession.add(models.Refdoctype(doctype_pk=dt.pk, ref_pk=ref.pk))
    if trigger:
        ref.ca_doctype_trigger = trigger

    return ref
