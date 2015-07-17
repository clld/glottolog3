# -*- coding: utf-8 -*-
"""
apply changes to the references in the db.

input:
- glottolog-data/scripts/monster-utf8.bib

output:
- glottolog-data/references/changes.json
"""
import re
from collections import Counter

import transaction

from clld.util import slug, jsondump
from clld.db.meta import DBSession
from clld.db.models.common import Source

from glottolog3.lib.bibtex import unescape
from glottolog3.models import Ref, Provider, Macroarea, Doctype, Languoid
from glottolog3.lib.util import get_map
from glottolog3.scripts.util import (
    update_providers, update_relationship, compute_pages, ca_trigger, get_args, get_bib,
)

NONREF_JSONDATA = {'gbs', 'internetarchive_id'}

FIELD_MAP = {
    'abstract': '',
    'added': '',
    'additional_items': '',
    'address': 'address',
    'adress': 'address',
    'adviser': '',
    'aiatsis_callnumber': '',
    'aiatsis_code': '',
    'aiatsis_reference_language': '',
    'anlanote': '',
    'anlclanguage': '',
    'anlctype': '',
    'annote': '',
    'asjp_name': '',
    'audiofile': '',
    'author': 'author',
    'author_note': '',
    'author_statement': '',
    'booktitle': 'booktitle',
    'booktitle_english': '',
    'bwonote': '',
    'call_number': '',
    'chapter': 'chapter',
    'citation': '',
    'class_loc': '',
    'collection': '',
    'comments': '',
    'contains_also': '',
    'copies': '',
    'copyright': '',
    'country': '',
    'coverage': '',
    'degree': '',
    'digital_formats': '',
    'document_type': '',
    'doi': '',
    'domain': '',
    'edition': 'edition',
    'edition_note': '',
    'editor': 'editor',
    'english_title': '',
    'extra_hash': '',
    'file': '',
    'fn': '',
    'fnnote': '',
    'folder': '',
    'format': '',
    'german_subject_headings': '',
    'glottolog_ref_id': '',
    'guldemann_location': '',
    'hhnote': '',
    'hhtype': '',
    'howpublished': 'howpublished',
    'inlg': 'inlg',
    'institution': '',
    'isbn': '',
    'issn': '',
    'issue': '',
    'journal': 'journal',
    'keywords': '',
    'langnote': '',
    'lapollanote': '',
    'last_changed': '',
    'lccn': '',
    'lcode': 'language_note',
    'lgcde': 'language_note',
    'lgcode': 'language_note',
    'lgcoe': 'language_note',
    'lgcosw': 'language_note',
    'lgfamily': '',
    'macro_area': '',
    'modified': '',
    'month': '',
    'mpi_eva_library_shelf': '',
    'mpifn': '',
    'no_inventaris': '',
    'note': 'note',
    'notes': 'note',
    'number': 'number',
    'numberofpages': '',
    'numner': 'number',
    'oages': 'pages',
    'omnote': '',
    'organization': 'organization',
    'other_editions': '',
    'otomanguean_heading': '',
    'ozbib_id': 'ozbib_id',
    'ozbibnote': '',
    'ozbibreftype': '',
    'paged': 'pages',
    'pages': 'pages',
    'pagex': 'pages',
    'permission': '',
    'pgaes': 'pages',
    'prepages': '',
    'publisher': 'publisher',
    'pubnote': '',
    'relatedresource': '',
    'reprint': '',
    'restrictions': '',
    'review': '',
    'school': 'school',
    'seanote': '',
    'seifarttype': '',
    'series': 'series',
    'series_english': '',
    'shelf_location': '',
    'shorttitle': '',
    'sil_id': '',
    'source': '',
    'src': '',
    'srctrickle': '',
    'stampeann': '',
    'stampedesc': '',
    'subject': 'subject',
    'subject_headings': 'subject_headings',
    'superseded': '',
    'thanks': '',
    'thesistype': '',
    'title': 'title',
    'title_english': '',
    'titlealt': '',
    'type': 'type',
    'umi_id': '',
    'url': 'url',
    'vernacular_title': '',
    'volume': 'volume',
    'volumr': 'volume',
    'weball_lgs': '',
    'year': 'year',
}

CONVERTER = {
    'ozbib_id': int,
    'url': lambda u, cmd=re.compile(r'^\\url\{(.*)\}$'): cmd.sub(r'\1', u),
}

PREF_YEAR_PATTERN = re.compile('\[(?P<year>(1|2)[0-9]{3})(\-[0-9]+)?\]')
YEAR_PATTERN = re.compile('(?P<year>(1|2)[0-9]{3})')
DOCTYPE_PATTERN = re.compile('(?P<name>[a-z\_]+)\s*(\((?P<comment>[^\)]+)\))?\s*(\;|$)')
CODE_PATTERN = re.compile('\[(?P<code>[^\]]+)\]')


def main(args):  # pragma: no cover
    stats = Counter(new=0, updated=0, skipped=0)
    changes = {}

    with transaction.manager:
        update_providers(args)
        DBSession.flush()
        provider_map = get_map(Provider)
        macroarea_map = get_map(Macroarea)
        doctype_map = get_map(Doctype)

        languoid_map = {}
        for l in DBSession.query(Languoid):
            if l.hid:
                languoid_map[l.hid] = l
            languoid_map[l.id] = l

        for i, rec in enumerate(get_bib(args)):
            if i and i % 1000 == 0:
                print i, 'records done', stats['updated'] + stats['new'], 'changed'

            if len(rec.keys()) < 6:
                # not enough information!
                stats.update(['skipped'])
                continue

            changed = False
            assert rec.get('glottolog_ref_id')
            id_ = int(rec.get('glottolog_ref_id'))

            ref = DBSession.query(Source).get(id_)
            update = True if ref else False

            kw = {
                'pk': id_,
                'bibtex_type': rec.genre,
                'id': str(id_),
                'jsondata': {'bibtexkey': rec.id},
            }

            for source, target in FIELD_MAP.items():
                if target is None:
                    continue
                value = rec.get(source)
                if value:
                    value = unescape(value)
                    if target:
                        kw[target] = CONVERTER.get(source, lambda x: x)(value)
                    else:
                        kw['jsondata'][source] = value

            if kw['jsondata'].get('hhtype'):
                trigger = ca_trigger(kw['jsondata']['hhtype'])
                if trigger:
                    kw['ca_doctype_trigger'], kw['jsondata']['hhtype'] = trigger

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

            if rec.get('numberofpages'):
                try:
                    kw['pages_int'] = int(rec.get('numberofpages').strip())
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

            for k in kw.keys():
                v = kw[k]
                if isinstance(v, basestring):
                    v = v.strip() or None
                kw[k] = v

            if update:
                for k in kw.keys():
                    if k == 'pk':
                        continue
                    v = getattr(ref, k)
                    if kw[k] != v:
                        if k == 'jsondata':
                            d = {k: v for k, v in ref.jsondata.items()
                                 if k in NONREF_JSONDATA}
                            d.update(**kw[k])
                            ref.jsondata = d
                        else:
                            #print k, '--', v
                            #print k, '++', kw[k]
                            setattr(ref, k, kw[k])
                            changed = True
                            if ref.id in changes:
                                changes[ref.id][k] = ('%s' % v, '%s' % kw[k])
                            else:
                                changes[ref.id] = {k: ('%s' % v, '%s' % kw[k])}
            else:
                changed = True
                ref = Ref(name='%s %s' % (kw.get('author', 'na'), kw.get('year', 'nd')), **kw)

            ref.description = ref.title or ref.booktitle
            originator = ref.author or ref.editor or 'Anonymous'
            ref.name = '%s %s' % (originator, ref.year or 'n.d.')

            a, r = update_relationship(
                ref.macroareas,
                [macroarea_map[name] for name in
                 set(filter(None, [s.strip() for s in kw['jsondata'].get('macro_area', '').split(',')]))])
            changed = changed or a or r

            src = [s.strip() for s in kw['jsondata'].get('src', '').split(',')]
            prv = {provider_map[slug(s)] for s in src if s}
            if set(ref.providers) != prv:
                ref.providers = list(prv)
                changed = True

            a, r = update_relationship(
                ref.doctypes,
                [doctype_map[m.group('name')] for m in
                 DOCTYPE_PATTERN.finditer(kw['jsondata'].get('hhtype', ''))])
            changed = changed or a or r

            if not update:
                stats.update(['new'])
                DBSession.add(ref)
            elif changed:
                stats.update(['updated'])

    args.log.info('%s' % stats)

    DBSession.execute("update source set description = title where description is null and title is not null;")
    DBSession.execute("update source set description = booktitle where description is null and booktitle is not null;")

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

    jsondump(changes, args.data_dir.joinpath('references', 'changes.json'))


if __name__ == '__main__':
    main(get_args())
