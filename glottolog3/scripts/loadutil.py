# coding: utf8
from __future__ import unicode_literals, print_function, division
import re

from clld.db.meta import DBSession
from clld.db.models import common
from clld.scripts.util import add_language_codes
from clld.lib.bibtex import EntryType
from clld.db.fts import tsvector
from clldutils.text import split_text
from clldutils.misc import slug

from glottolog3 import models
from glottolog3.scripts.util import compute_pages

PREF_YEAR_PATTERN = re.compile('\[(?P<year>(1|2)[0-9]{3})(\-[0-9]+)?\]')
YEAR_PATTERN = re.compile('(?P<year>(1|2)[0-9]{3})')


def add_identifier(languoid, data, name, type, description, lang='en'):
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
        bookkeeping=lang.category == 'Bookkeeping',
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
    kw = {'jsondata': {}}
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
        fts=tsvector('\n'.join(v for k, v in entry.fields.items() if k != 'abstract')),
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
