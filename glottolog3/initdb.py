from collections import defaultdict, OrderedDict
from time import time
import functools

import attr
import purl
from clld.scripts.util import Data, add_language_codes
from clld.db.meta import DBSession
from clld.db.models import common
from clld.db import fts
from clld.lib.bibtex import EntryType
from clldutils import jsonlib
from clldutils.text import split_text
from clldutils.apilib import assert_release
from sqlalchemy.orm import joinedload

from pyglottolog.references import BibFile

from glottolog3 import models
from glottolog3.scripts.util import (
    recreate_treeclosure, idjoin, add_parameter, split_items, add_identifiers, add_values,
    read_macroarea_geojson,
)


def gc2version(args):
    return args.pkg_dir.parent / 'archive' / 'glottocode2version.json'


def load(args):
    glottolog = args.repos
    fts.index('fts_index', models.Ref.fts, DBSession.bind)
    DBSession.execute("CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA public;")
    version = assert_release(glottolog.repos)
    dataset = common.Dataset(
        id='glottolog',
        name="{0} {1}".format(glottolog.publication.web.name, version),
        publisher_name=glottolog.publication.publisher.name,
        publisher_place=glottolog.publication.publisher.place,
        publisher_url=glottolog.publication.publisher.url,
        license=glottolog.publication.license.url,
        domain=purl.URL(glottolog.publication.web.url).domain(),
        contact=glottolog.publication.web.contact,
        jsondata={'license_icon': 'cc-by.png', 'license_name': glottolog.publication.license.name},
    )
    data = Data()

    for e in glottolog.editors.values():
        if e.current:
            ed = data.add(common.Contributor, e.id, id=e.id, name=e.name)
            common.Editor(dataset=dataset, contributor=ed, ord=int(e.ord))
    DBSession.add(dataset)

    contrib = data.add(common.Contribution, 'glottolog', id='glottolog', name='Glottolog')
    DBSession.add(common.ContributionContributor(
        contribution=contrib, contributor=data['Contributor']['hammarstroem']))

    #
    # Add Parameters:
    #
    add = functools.partial(add_parameter, data)
    add('fc', name='Family classification')
    add('sc', name='Subclassification')
    add('aes',
        args.repos.aes_status.values(),
        name=args.repos.aes_status.__defaults__['name'],
        pkw=dict(
            jsondata=dict(
                reference_id=args.repos.aes_status.__defaults__['reference_id'],
                sources=[attr.asdict(v) for v in args.repos.aes_sources.values()],
                scale=[attr.asdict(v) for v in args.repos.aes_status.values()])),
        dekw=lambda de: dict(name=de.name, number=de.ordinal, jsondata=dict(icon=de.icon)),
    )
    add('med',
        args.repos.med_types.values(),
        name='Most Extensive Description',
        dekw=lambda de: dict(
            name=de.name, description=de.description, number=de.rank, jsondata=dict(icon=de.icon)),
    )
    add('macroarea',
        args.repos.macroareas.values(),
        pkw=dict(
            description=args.repos.macroareas.__defaults__['description'],
            jsondata=dict(reference_id=args.repos.macroareas.__defaults__['reference_id'])),
        dekw=lambda de: dict(
            name=de.name,
            description=de.description,
            jsondata=dict(geojson=read_macroarea_geojson(args.repos, de.name, de.description)),
        ),
    )
    add('ltype',
        args.repos.language_types.values(),
        name='Language Type',
        dekw=lambda de: dict(name=de.category, description=de.description),
        delookup='category',
    )
    add('country',
        args.repos.countries,
        dekw=lambda de: dict(name=de.id, description=de.name),
    )

    legacy = jsonlib.load(gc2version(args))
    for gc, version in legacy.items():
        data.add(models.LegacyCode, gc, id=gc, version=version)

    #
    # Now load languoid data, keeping track of relations that can only be inserted later.
    #
    lgsources = defaultdict(list)
    # Note: We rely on languoids() yielding languoids in the "right" order, i.e. such that top-level
    # nodes will precede nested nodes. This order must be preserved using an `OrderedDict`:
    nodemap = OrderedDict([(l.id, l) for l in glottolog.languoids()])
    lgcodes = {k: v.id for k, v in args.repos.languoids_by_code(nodemap).items()}
    for lang in nodemap.values():
        for ref in lang.sources:
            lgsources['{0.provider}#{0.bibkey}'.format(ref)].append(lang.id)
        load_languoid(glottolog, data, lang, nodemap)

    for gc in glottolog.glottocodes:
        if gc not in data['Languoid'] and gc not in legacy:
            common.Config.add_replacement(gc, None, model=common.Language)

    for obj in jsonlib.load(glottolog.references_path('replacements.json')):
        common.Config.add_replacement(
            '{0}'.format(obj['id']),
            '{0}'.format(obj['replacement']) if obj['replacement'] else None,
            model=common.Source)

    DBSession.flush()

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
            BibFile(glottolog.build_path('monster-utf8.bib'), api=glottolog).iterentries()):
        if i % 10000 == 0:
            args.log.info('{0}: {1:.3}'.format(i, time() - s))
            s = time()
        ref = load_ref(data, entry, lgcodes, lgsources)
        if 'macro_area' in entry.fields:
            mas = []
            for ma in split_text(entry.fields['macro_area'], separators=',;', strip=True):
                ma = 'North America' if ma == 'Middle America' else ma
                ma = glottolog.macroareas.get('Papunesia' if ma == 'Papua' else ma)
                mas.append(ma.name)
            ref.macroareas = ', '.join(mas)


def prime(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
    #
    # Now that we loaded all languoids and refs, we can compute the MED values.
    #
    meds = defaultdict(list)
    for lpk, spk, sid, sname, med_type, year, pages in DBSession.execute("""\
select
  l.pk, r.pk, s.id, s.name, r.med_type, s.year_int, r.med_pages
from
  languagesource as ls,
  language as l,
  source as s,
  ref as r
where
  ls.active = TRUE and l.pk = ls.language_pk and s.pk = ls.source_pk and s.pk = r.pk
order by
  l.id, r.med_index desc, r.med_pages, coalesce(s.year_int, 0), s.pk
"""):
        meds[lpk].append((spk, sid, sname, med_type, year, pages))  # The last one is the overall MED

    # Now weed out the "newer but worse" sources:
    for lpk, sources in {k: reversed(v) for k, v in meds.items()}.items():
        relevant, lastyear = [], 10000
        for spk, sid, sname, med_type, year, pages in sources:
            if year and year < lastyear:  # If year is more recent, this is a "newer but worse" item
                relevant.append((spk, sid, sname, med_type, year, pages))
                lastyear = year
        meds[lpk] = relevant

    med_param = common.Parameter.get('med')
    med_domain = {de.id: de for de in med_param.domain}
    contrib = common.Contribution.get('glottolog')

    for l in DBSession.query(common.Language).filter(common.Language.pk.in_(list(meds.keys()))):
        l.update_jsondata(meds=[
            (sid, med_type, year, pages, sname) for spk, sid, sname, med_type, year, pages in meds[l.pk]])
        if not meds[l.pk]:
            continue

        med = meds[l.pk][0]
        # Record the overall MED as value for the 'med' Parameter:
        vs = common.ValueSet(
            id=idjoin('med', l.id),
            contribution=contrib,
            parameter=med_param,
            language=l,
        )
        DBSession.add(common.Value(
            id=idjoin('med', l.id),
            name=getattr(args.repos.med_types, med[3]).name,
            domainelement=med_domain[idjoin('med', med[3])],
            valueset=vs,
        ))
        DBSession.flush()
        DBSession.add(common.ValueSetReference(source_pk=med[0], valueset_pk=vs.pk))

    recreate_treeclosure()

    macroareas = {r[0]: (r[1], r[2]) for r in DBSession.execute("""\
select de.pk, de.id, de.name
from domainelement as de, parameter as p
where de.parameter_pk = p.pk and p.id = 'macroarea'
""")}

    for lid, lpk, cpk, ppk, mas in DBSession.execute("""\
select
  l.id, l.pk, vs.contribution_pk, vs.parameter_pk, array_agg(distinct v.domainelement_pk)
from
  language as l,
  treeclosuretable as t,
  parameter as p,
  valueset as vs,
  value as v
where
  l.pk = t.parent_pk and
  t.child_pk = vs.language_pk and
  vs.parameter_pk = p.pk and
  p.id = 'macroarea' and
  v.valueset_pk = vs.pk and
  l.pk not in (
    select language_pk 
    from valueset as _vs, parameter as _p 
    where _vs.parameter_pk = _p.pk and _p.id = 'macroarea'
  )
group by l.id, l.pk, vs.contribution_pk, vs.parameter_pk"""):
        for i, mapk in enumerate(mas):
            if i == 0:
                vs = common.ValueSet(
                    id=idjoin('macroarea', lid),
                    language_pk=lpk,
                    parameter_pk=ppk,
                    contribution_pk=cpk)
            DBSession.add(common.Value(
                id=idjoin(macroareas[mapk][0], lid),
                name=macroareas[mapk][1],
                domainelement_pk=mapk,
                valueset=vs))

    for vs in DBSession.query(common.ValueSet)\
            .join(common.Language)\
            .join(common.Parameter)\
            .filter(common.Parameter.id == 'macroarea')\
            .options(joinedload(common.ValueSet.values), joinedload(common.ValueSet.language)):
        vs.language.macroareas = ', '.join([macroareas[v.domainelement_pk][1] for v in vs.values])

    for row in list(DBSession.execute(
        "select pk, pages, pages_int, startpage_int from source where pages_int < 0"
    )):
        raise ValueError(row)

    version = assert_release(args.repos.repos)
    with jsonlib.update(gc2version(args), indent=4) as legacy:
        for lang in DBSession.query(common.Language):
            if lang.id not in legacy:
                lang.update_jsondata(new=True)
                legacy[lang.id] = version

    valuesets = {
        r[0]: r[1] for r in DBSession.query(common.ValueSet.id, common.ValueSet.pk)}
    refs = {
        r[0]: r[1]
        for r in DBSession.query(models.Refprovider.id, models.Refprovider.ref_pk)}

    for vsid, vspk in valuesets.items():
        if vsid.startswith('macroarea-'):
            DBSession.add(common.ValueSetReference(
                source_pk=refs[args.repos.macroareas.__defaults__['reference_id']],
                valueset_pk=vspk))

    for vs in DBSession.query(common.ValueSet)\
            .join(common.Parameter)\
            .filter(common.Parameter.id == 'aes'):
        if vs.jsondata['reference_id']:
            DBSession.add(common.ValueSetReference(
                source_pk=refs[vs.jsondata['reference_id']], valueset_pk=vs.pk))

    for lang in args.repos.languoids():
        if lang.category == args.repos.language_types.bookkeeping.category:
            continue
        clf = lang.classification_comment
        if clf:
            for pid, attr_ in [('sc', 'sub'), ('fc', 'family')]:
                if getattr(clf, attr_ + 'refs'):
                    if split_items(lang.cfg['classification'][attr_ + 'refs']) != \
                            split_items(lang.cfg['classification'].get(attr_)):
                        vspk = valuesets['{0}-{1}'.format(pid, lang.id)]
                        for ref in getattr(clf, attr_ + 'refs'):
                            spk = refs.get(ref.key)
                            if spk:
                                DBSession.add(
                                    common.ValueSetReference(source_pk=spk, valueset_pk=vspk))


def load_languoid(glottolog, data, lang, nodemap):
    """
    Load data from one Languoid object.

    :param glottolog: A `pyglottolog.Glottolog` instance.
    :param data: A `dict` providing access to previously loaded data.
    :param lang: The `pyglottolog.languoids.Languoid` object.
    :param nodemap: A `dict` mapping glottocodes to `pyglottolog.languoids.Languoid`s.
    :return:
    """
    dblang = data.add(
        models.Languoid,
        lang.id,
        id=lang.id,
        hid=lang.hid,
        name=lang.name,
        bookkeeping=lang.category == glottolog.language_types.bookkeeping.category,
        category=lang.category,
        newick=lang.newick_node(nodemap).newick,
        latitude=lang.latitude,
        longitude=lang.longitude,
        level=models.LanguoidLevel.from_string(lang.level.name),
        father=data['Languoid'][lang.lineage[-1][1]] if lang.lineage else None,
        jsondata=dict(
            iso_retirement=lang.iso_retirement.__json__() if lang.iso_retirement else None,
            ethnologue_comment=lang.ethnologue_comment.__json__()
            if lang.ethnologue_comment else None,
            links=[l.__json__() for l in lang.links],
        )
    )
    if lang.iso:
        add_language_codes(data, dblang, lang.iso)

    add_identifiers(data, dblang, lang.names, name_type=True)
    add_identifiers(data, dblang, lang.identifier, name_type=False)

    add = functools.partial(add_values, data, dblang)
    add('macroarea', [(m.id, m.name) for m in lang.macroareas])
    add('country', [(c.id, c.name) for c in lang.countries])
    if lang.endangerment:
        add('aes',
            [(lang.endangerment.status.id, lang.endangerment.status.name)],
            source=lang.endangerment.source.name,
            jsondata=attr.asdict(lang.endangerment.source),
            description=lang.endangerment.comment,
        )
    if lang.level == glottolog.languoid_levels.language:
        add('ltype', [(lang.category, lang.category)])

    if not dblang.bookkeeping:
        # Languages in Bookkeeping do not have a meaningful classification!
        clf = lang.classification_comment
        if clf:
            for attr_, pid in [('sub', 'sc'), ('family', 'fc')]:
                val = getattr(clf, attr_)
                if not val:
                    val = getattr(clf, attr_ + 'refs')
                    if val:
                        val = ', '.join('{0}'.format(r) for r in val)
                if val:
                    add(pid, [('1', '')], with_de=False, description=val)


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

    kw.update(
        publisher=entry.publisher_and_address[0],
        address=entry.publisher_and_address[1],
        year_int=entry.year_int,
        pages_int=entry.pages_int,
        med_index=-entry.weight[0],
        med_pages=entry.weight[1],
        med_type=entry.med_type.id,
        id=entry.fields['glottolog_ref_id'],
        fts=fts.tsvector('\n'.join(v for k, v in entry.fields.items() if k != 'abstract')),
        name='{} {}'.format(entry.fields.get('author', 'na'), entry.fields.get('year', 'nd')),
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
            reflangs.extend(lgsources.get(key, []))
            prov, key = key.split('#', 1)
            provs.add(prov)
            DBSession.add(models.Refprovider(
                provider_pk=data['Provider'][prov].pk,
                ref_pk=ref.pk,
                id='{0}:{1}'.format(prov, key)))

    if not reflangs:
        reflangs, trigger = entry.languoids(lgcodes)
        if trigger and ((provs in no_ca) or (reflangs)):
            # Discard computerized assigned languoids for bibs where this does not make sense,
            # or for bib entries that have been manually assigned in a Languoid's ini file.
            reflangs, trigger = [], None

    for lid in set(reflangs):
        DBSession.add(
            common.LanguageSource(
                language_pk=data['Languoid'][lid].pk, source_pk=ref.pk, active=not bool(trigger)))
    if trigger:
        ref.ca_language_trigger = trigger

    doctypes, trigger = entry.doctypes(data['Doctype'])
    if trigger is None or provs not in no_ca:
        for dt in set(doctypes):
            DBSession.add(models.Refdoctype(doctype_pk=dt.pk, ref_pk=ref.pk))
    if trigger:
        ref.ca_doctype_trigger = trigger

    return ref
