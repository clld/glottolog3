import sys
import re
import json
import random

import transaction

from sqlalchemy import desc, or_
from sqlalchemy.orm import joinedload
from clld.lib.bibtex import Database, EntryType
from clld.util import UnicodeMixin, slug
from clld.scripts.util import parsed_args
from clld.db.meta import DBSession
from clld.db.models.common import Source

from glottolog3.lib.util import roman_to_int
from glottolog3.lib.bibtex import unescape
from glottolog3.models import (
    Ref, Provider, Refprovider, Macroarea, Doctype, Country, Languoid,
)
from glottolog3.lib.util import get_map

# id
# bibtexkey
# type
# startpage              | integer           |
# endpage                | integer           |
# numberofpages          | integer           |

# bibtexkey              | text              | not null
# type                   | text              | not null
# inlg_code              | text              |
# year                   | integer           |
# jsondata               | character varying |

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
    'alnumcodes': '',
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
    'citation': '',
    'class_loc': '',
    'collection': '',
    'comments': '',
    'contains_also': '',
    'contributed': '',
    'copies': '',
    'copyright': '',
    'country': '',
    'coverage': '',
    'crossref': '',
    'de': '',
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
    'extrahash': '',
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
    'howpublished': '',
    'id': '',
    'inlg': 'inlg',
    'institution': '',
    'isbn': '',
    'issn': '',
    'issue': '',
    'jfmnote': '',
    'journal': 'journal',
    'key': '',
    'keywords': '',
    'langcode': '',
    'langnote': '',
    'languoidbase_ids': '',
    'lapollanote': '',
    'last_changed': '',
    'lccn': '',
    'lcode': '',
    'lgcde': '',
    'lgcode': '',
    'lgcoe': '',
    'lgcosw': '',
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
    'oldhhfn': '',
    'oldhhfnnote': '',
    'omnote': '',
    'other_editions': '',
    'otomanguean_heading': '',
    'owner': '',
    'ozbib_id': 'ozbib_id',
    'ozbibnote': '',
    'ozbibreftype': '',
    'paged': 'pages',
    'pages': 'pages',
    'pagex': 'pages',
    'permission': '',
    'pgaes': 'pages',
    'phdthesis': '',
    'prepages': '',
    'publisher': 'publisher',
    'pubnote': '',
    'rating': '',
    'read': '',
    'relatedresource': '',
    'replication': '',
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
    'status': '',
    'subject': 'subject',
    'subject_headings': 'subject_headings',
    'subsistence_note': '',
    'superseded': '',
    'thanks': '',
    'thesistype': '',
    'timestamp': '',
    'title': 'title',
    'title_english': '',
    'titlealt': '',
    'typ': '',
    'umi_id': '',
    'url': 'url',
    'vernacular_title': '',
    'volume': 'volume',
    'volumr': 'volume',
    'weball_lgs': '',
    'year': 'year',
    'yeartitle': '',
}

CONVERTER = {'ozbib_id': int}

YEAR_PATTERN = re.compile('(?P<year>(1|2)[0-9]{3})')
ROMAN = '(?P<roman>[ivxlcdmIVXLCDM]+)'
ARABIC = '(?P<arabic>[0-9]+)'
ROMANPAGESPATTERNra = re.compile(u'%s\+%s' % (ROMAN, ARABIC))
ROMANPAGESPATTERNar = re.compile(u'%s\+%s' % (ARABIC, ROMAN))
PAGES_PATTERN = re.compile('(?P<start>[0-9]+)\s*\-\-?\s*(?P<end>[0-9]+)')
DOCTYPE_PATTERN = re.compile('(?P<name>[a-z\_]+)\s*(\((?P<comment>[^\)]+)\))?\s*(\;|$)')
CODE_PATTERN = re.compile('\[(?P<code>[^\]]+)\]')


#
# TODO: implement three modes: compare, import, update
#

def main(bib, mode):  # pragma: no cover
    count = 0
    skipped = 0

    with transaction.manager:
        provider_map = get_map(Provider)
        macroarea_map = get_map(Macroarea)
        doctype_map = get_map(Doctype)

        known_ids = set(r[0] for r in DBSession.query(Ref.pk))

        languoid_map = {}
        for l in DBSession.query(Languoid):
            if l.hid:
                languoid_map[l.hid] = l
            languoid_map[l.id] = l

        for i, rec in enumerate(bib):
            if len(rec.keys()) < 6:
                skipped += 1
                #print '---> skip', rec.id
                #print rec
                continue

            changed = False
            assert rec.get('glottolog_ref_id')
            id_ = int(rec.get('glottolog_ref_id'))
            if mode != 'update' and id_ in known_ids:
                continue
            ref = DBSession.query(Source).get(id_)
            update = True if ref else False

            kw = {
                'pk': id_,
                'bibtex_type': getattr(EntryType, rec.genre),
                'id': str(id_),
                'jsondata': {'bibtexkey': rec.id},
            }

            for source, target in FIELD_MAP.items():
                value = rec.get(source)
                if value:
                    value = unescape(value)
                    if target:
                        kw[target] = CONVERTER.get(source, lambda x: x)(value)
                    else:
                        kw['jsondata'][source] = value

            # try to extract numeric year, startpage, endpage, numberofpages, ...
            if rec.get('numberofpages'):
                try:
                    kw['pages_int'] = int(rec.get('numberofpages').strip())
                except ValueError:
                    pass

            if kw.get('year'):
                match = YEAR_PATTERN.search(kw.get('year'))
                if match:
                    kw['year_int'] = int(match.group('year'))

            if kw.get('publisher'):
                p = kw.get('publisher')
                if ':' in p:
                    address, publisher = [s.strip() for s in kw['publisher'].split(':', 1)]
                    if not 'address' in kw or kw['address'] == address:
                        kw['address'], kw['publisher'] = address, publisher

            if kw.get('pages'):
                pages = kw.get('pages')
                match = ROMANPAGESPATTERNra.search(pages)
                if not match:
                    match = ROMANPAGESPATTERNar.search(pages)
                if match:
                    if 'pages_int' not in kw:
                        kw['pages_int'] = roman_to_int(match.group('roman')) \
                            + int(match.group('arabic'))
                else:
                    start = None
                    number = None
                    match = None

                    for match in PAGES_PATTERN.finditer(pages):
                        if start is None:
                            start = int(match.group('start'))
                        number = (number or 0) \
                            + (int(match.group('end')) - int(match.group('start')) + 1)

                    if match:
                        kw['endpage_int'] = int(match.group('end'))
                        kw['startpage_int'] = start
                        kw.setdefault('pages_int', number)
                    else:
                        try:
                            kw['startpage_int'] = int(pages)
                        except ValueError:
                            pass

            if update:
                for k in kw.keys():
                    if k == 'pk':
                        continue
                    #if k == 'title':
                    #    v = ref.title or ref.description
                    #else:
                    if 1:
                        v = getattr(ref, k)
                    if kw[k] != v:
                        #
                        # TODO!
                        #
                        setattr(ref, k, kw[k])
                        #if k not in ['jsondata', 'publisher']:
                        #    print k, ref.pk
                        #    print kw[k]
                        #    print v
                        #    print '--------------'
                        changed = True
                    if ref.title:
                        ref.description = ref.title
            else:
                changed = True
                ref = Ref(**kw)

            def append(attr, obj):
                if obj and obj not in attr:
                    changed = True
                    #
                    # TODO!
                    #
                    attr.append(obj)

            for name in set(filter(None, [s.strip() for s in kw['jsondata'].get('macro_area', '').split(',')])):
                append(ref.macroareas, macroarea_map[name])

            for name in set(filter(None, [s.strip() for s in kw['jsondata'].get('src', '').split(',')])):
                append(ref.providers, provider_map[slug(name)])

            for m in DOCTYPE_PATTERN.finditer(kw['jsondata'].get('hhtype', '')):
                append(ref.doctypes, doctype_map[m.group('name')])

            if len(kw['jsondata'].get('lgcode', '')) == 3:
                kw['jsondata']['lgcode'] = '[%s]' % kw['jsondata']['lgcode']

            for m in CODE_PATTERN.finditer(kw['jsondata'].get('lgcode', '')):
                for code in set(m.group('code').split(',')):
                    if code not in languoid_map:
                        if code not in ['NOCODE_Payagua', 'emx']:
                            print '--> unknown code:', code.encode('utf8')
                    else:
                        append(ref.languages, languoid_map[code])

            for glottocode in filter(None, kw['jsondata'].get('alnumcodes', '').split(';')):
                if glottocode not in languoid_map:
                    print '--> unknown glottocode:', glottocode.encode('utf8')
                else:
                    append(ref.languages, languoid_map[glottocode])

            if not update:
                #pass
                #
                # TODO!
                #
                DBSession.add(ref)

            if i % 100 == 0:
                print i, 'records done'

            if changed:
                count += 1

        print count, 'records updated or imported'
        print skipped, 'records skipped because of lack of information'


if __name__ == '__main__':
    args = parsed_args((('--mode',), dict(default='insert')))
    main(Database.from_file(args.data_file('refs.bib'), encoding='utf8'), args.mode)
