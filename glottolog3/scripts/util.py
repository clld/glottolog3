from __future__ import unicode_literals, print_function
import io
import re
import json
from six.moves.configparser import RawConfigParser

from sqlalchemy import sql, desc, not_, or_

from clld.db.meta import DBSession
from clld.util import slug
from clld.lib.bibtex import Database
from clld.db.models.common import Source, Language_data
from clld.db.util import page_query, icontains

from glottolog3.lib.util import get_map, roman_to_int
from glottolog3.lib.bibtex import unescape
from glottolog3.models import Ref, Languoid, TreeClosureTable, Provider, LanguoidLevel


WORD_PATTERN = re.compile('[a-z]+')
SQUARE_BRACKET_PATTERN = re.compile('\[(?P<content>[^\]]+)\]')
CODE_PATTERN = re.compile('(?P<code>[a-z]{3}|NOCODE_[\w\-]+)|[a-z][a-z0-9]{3}[1-9]\d{3}$')
ROMAN = '[ivxlcdmIVXLCDM]+'
ROMANPATTERN = re.compile(ROMAN + '$')
ARABIC = '[0-9]+'
ARABICPATTERN = re.compile(ARABIC + '$')
SEPPAGESPATTERN = re.compile(
    '(?P<n1>{0}|{1})\s*(,|;|\.|\+|/)\s*(?P<n2>{0}|{1})'.format(ROMAN, ARABIC))
PAGES_PATTERN = re.compile(
    '(?P<start>{0}|{1})\s*\-\-?\s*(?P<end>{0}|{1})'.format(ROMAN, ARABIC))
CA_PATTERN = re.compile('\(computerized assignment from \"(?P<trigger>[^\"]+)\"\)')
ART_NO_PATTERN = re.compile('\(art\.\s*[0-9]+\)')


def ca_trigger(s):
    """
    :return: pair (trigger, updated s) or None.
    """
    m = CA_PATTERN.search(s)
    if m:
        return m.group('trigger'), (s[:m.start()] + s[m.end():]).strip()


def get_int(s):
    s = s.strip()
    try:
        return int(s)
    except ValueError:
        if ROMANPATTERN.match(s):
            return roman_to_int(s)


def compute_pages(pages):
    """
    >>> compute_pages('x+23')
    (None, None, 33)
    >>> compute_pages('x + 23')
    (None, None, 33)
    >>> compute_pages('x. 23')
    (None, None, 33)
    >>> compute_pages('23,xi')
    (None, None, 34)
    >>> compute_pages('23,ix')
    (None, None, 32)
    >>> compute_pages('ix')
    (1, 9, 9)
    >>> compute_pages('12-45')
    (12, 45, 34)
    >>> compute_pages('125-9')
    (125, 129, 5)
    >>> compute_pages('7-3')
    (3, 7, 5)
    """
    pages = ART_NO_PATTERN.sub('', pages)
    pages = pages.strip().replace('\u2013', '-')
    if pages.endswith('.'):
        pages = pages[:-1]
    if pages.endswith('pp'):
        pages = pages[:-2]

    # trivial case: just one number:
    n = get_int(pages)
    if n:
        return (1, n, n)

    # next case: ,|.|+ separated numbers:
    m = SEPPAGESPATTERN.match(pages)
    if m:
        return (None, None, sum(map(get_int, [m.group('n1'), m.group('n2')])))

    # next case: ranges:
    start = None
    end = None
    number = None

    for match in PAGES_PATTERN.finditer(pages):
        s_start, s_end = match.group('start'), match.group('end')
        s, e = get_int(s_start), get_int(s_end)
        if ARABICPATTERN.match(s_end) and ARABICPATTERN.match(s_start) \
                and len(s_end) < len(s_start):
            # the case 516-32:
            s_end = s_start[:-len(s_end)] + s_end
            e = get_int(s_end)
        if s > e:
            # the case 532-516:
            e, s = s, e
        if start is None:
            start = s
        end = e
        number = (number or 0) + (end - s + 1)

    return (start, end, number if number > 0 else None)


def update_relationship(col, new, log=None, log_only=False):
    added, removed = 0, 0
    old = set(item for item in col)
    new = set(new)
    for item in old - new:
        removed += 1
        if not log_only:
            col.remove(item)
        if log:
            log.info('--')
    for item in new - old:
        added += 1
        if not log_only:
            col.append(item)
        if log:
            log.info('++')
    return added, removed


def get_obsolete_refs(args):
    """compute all refs that no longer have an equivalent in the bib file.
    """
    bib = Database.from_file(args.data_file(args.version, 'refs.bib'), encoding='utf8')
    known_ids = {rec['glottolog_ref_id']: 1 for rec in bib}
    return [(row[0], row[1]) for row in
            DBSession.query(Ref.id, Ref.name)
            .filter(not_(icontains(Ref.name, 'ISO 639-3 Registration Authority')))
            if row[0] not in known_ids]


def match_obsolete_refs(args, refs):
    matched = {}

    #
    # TODO: optionally re-evaluate known-unmatched refs!
    #
    refs = [r[0] for r in refs]
    count = 0
    f, m = 0, 0
    for id_ in refs:
        if id_ in matched:
            continue
        count += 1
        if count > 1000:
            print('1000 obsolete refs processed!')
            break
        ref = Ref.get(id_)
        found = False
        if ref.description and len(ref.description) > 5:
            for match in DBSession.query(Ref)\
                    .filter(not_(Source.id.in_(refs)))\
                    .filter(Source.description.contains(ref.description))\
                    .filter(or_(Source.author == ref.author, Source.year == ref.year))\
                    .limit(10):
                print('++', ref.id, '->', match.id, '++', ref.author, '->', match.author, '++', ref.year, '->', match.year)
                matched[ref.id] = match.id
                found = True
                break
            if not found and ref.name and len(ref.name) > 5:
                for match in DBSession.query(Ref)\
                        .filter(not_(Source.id.in_(refs)))\
                        .filter(Source.name == ref.name)\
                        .limit(10):
                    try:
                        if match.description and ref.description and slug(match.description) == slug(ref.description):
                            print('++', ref.id, '->', match.id, '++', ref.description, '->', match.description)
                            matched[ref.id] = match.id
                            found = True
                            break
                    except AssertionError:
                        continue
        if not found:
            m += 1
            print('--', ref.id, ref.name, ref.description)
            matched[ref.id] = None
        else:
            f += 1
    print(f, 'found')
    print(m, 'missed')
    return matched


def get_codes(ref):
    """detect language codes in a string

    known formats:
    - cul
    - cul, Culina [cul]
    - cul, aka
    - [cul, aka, NOCODE_Culina]
    """
    # look at everything in square brackets
    for match in SQUARE_BRACKET_PATTERN.finditer(ref.language_note):
        # then split by comma, and look at the parts
        for code in [s.strip() for s in match.group('content').split(',')]:
            if CODE_PATTERN.match(code):
                yield code


def update_reflang(args):
    with open(args.data_file('brugmann_noderefs.json')) as fp:
        brugmann_noderefs = json.load(fp)

    ignored, obsolete, changed, unknown = 0, 0, 0, {}
    languoid_map = {}
    for l in DBSession.query(Languoid):
        if l.hid:
            languoid_map[l.hid] = l.pk
        languoid_map[l.id] = l.pk

    lgcodes = {}
    for rec in Database.from_file(
            args.data_file(args.version, 'refs.bib'), encoding='utf8'):
        lgcode = ''
        for f in 'lgcode lcode lgcde lgcoe lgcosw'.split():
            if rec.get(f):
                lgcode = rec[f]
                break
        if len(lgcode) == 3 or lgcode.startswith('NOCODE_'):
            lgcode = '[' + lgcode + ']'
        lgcodes[rec.get('glottolog_ref_id', None)] = lgcode

    #for ref in DBSession.query(Ref).order_by(desc(Source.pk)).limit(10000):
    for ref in page_query(
            DBSession.query(Ref).order_by(desc(Source.pk)),
            n=10000,
            commit=True,
            verbose=True):
        # disregard iso change requests:
        if ref.description and ref.description.startswith('Change Request Number '):
            ignored += 1
            continue

        if ref.id not in lgcodes:
            # remove all language relations for refs no longer in bib!
            update_relationship(ref.languages, [])
            obsolete += 1
            continue

        language_note = lgcodes[ref.id]
        trigger = ca_trigger(language_note)
        if trigger:
            ref.ca_language_trigger, ref.language_note = trigger
        else:
            ref.language_note = language_note

        remove = brugmann_noderefs['delete'].get(str(ref.pk), [])

        # keep relations to non-language languoids:
        langs = [
            l for l in ref.languages if
            (l.level != LanguoidLevel.language or not l.active) and l.pk not in remove]
        langs_pk = [l.pk for l in langs]

        # add relations from filemaker data:
        for lpk in brugmann_noderefs['create'].get(str(ref.pk), []):
            if lpk not in langs_pk:
                l = Languoid.get(lpk, default=None)
                if l:
                    #print('relation added according to brugmann data')
                    langs.append(l)
                    langs_pk.append(l.pk)
                else:
                    print('brugmann relation for non-existing languoid')

        for code in set(get_codes(ref)):
            if code not in languoid_map:
                unknown[code] = 1
                continue
            lpk = languoid_map[code]
            if lpk in remove:
                print(ref.name, ref.id, '--', l.name, l.id)
                print('relation removed according to brugmann data')
            else:
                if lpk not in langs_pk:
                    langs.append(DBSession.query(Languoid).get(lpk))
                    langs_pk.append(lpk)

        a, r = update_relationship(ref.languages, langs)
        if a or r:
            changed += 1

    print(ignored, 'ignored')
    print(obsolete, 'obsolete')
    print(changed, 'changed')
    print('unknown codes', unknown.keys())


def recreate_treeclosure(session=None):
    """Denormalize ancestry, top-level and descendant counts for languoids."""
    if session is None:
        session = DBSession
    session.execute(TreeClosureTable.__table__.delete())
    sql = ["""WITH RECURSIVE tree(child_pk, parent_pk, depth) AS (
      SELECT pk, pk, 0 FROM languoid
    UNION ALL
      SELECT t.child_pk, p.father_pk, t.depth + 1
      FROM languoid AS p
      JOIN tree AS t ON p.pk = t.parent_pk
      WHERE p.father_pk IS NOT NULL
    )
    INSERT INTO treeclosuretable (created, updated, active, child_pk, parent_pk, depth)
    SELECT now(), now(), true, * FROM tree""",
    """UPDATE languoid AS l SET family_pk = u.family_pk
    FROM (WITH RECURSIVE tree(child_pk, parent_pk, depth) AS (
      SELECT pk, father_pk, 1 FROM languoid
    UNION ALL
      SELECT t.child_pk, p.father_pk, t.depth + 1
      FROM languoid AS p
      JOIN tree AS t ON p.pk = t.parent_pk
      WHERE p.father_pk IS NOT NULL
    )
    SELECT DISTINCT ON (child_pk) child_pk, parent_pk AS family_pk
    FROM tree ORDER BY child_pk, depth DESC) AS u
    WHERE l.pk = u.child_pk AND l.family_pk IS DISTINCT FROM u.family_pk""",
    """UPDATE languoid AS l SET
      child_family_count = u.child_family_count,
      child_language_count = u.child_language_count,
      child_dialect_count = u.child_dialect_count
    FROM (WITH RECURSIVE tree(child_pk, parent_pk, level) AS (
      SELECT pk, father_pk, level FROM languoid
    UNION ALL
      SELECT t.child_pk, p.father_pk, t.level
      FROM languoid AS p
      JOIN tree AS t ON p.pk = t.parent_pk
      WHERE p.father_pk IS NOT NULL
    )
    SELECT pk,
      count(nullif(tree.level != 'family', true)) AS child_family_count,
      count(nullif(tree.level != 'language', true)) AS child_language_count,
      count(nullif(tree.level != 'dialect', true)) AS child_dialect_count
    FROM languoid LEFT JOIN tree ON pk = tree.parent_pk
    GROUP BY pk) AS u
    WHERE l.pk = u.pk AND (
      l.child_family_count != u.child_family_count OR
      l.child_language_count != u.child_language_count OR
      l.child_dialect_count != u.child_dialect_count)"""]
    for s in sql:
        session.execute(s)
    session.execute('COMMIT')


def update_providers(args, filename='BIBFILES.ini'):
    filepath = args.data_file(args.version, filename)
    if not filepath.exists():
        return

    p = RawConfigParser()
    with io.open(filepath, encoding='utf-8-sig') as fp:
        p.readfp(fp)

    provider_map = get_map(Provider)
    for section in p.sections():
        sectname = section[:-4] if section.endswith('.bib') else section
        id_ = slug(sectname)
        name = p.get(section, 'title')
        description = p.get(section, 'description')
        abbr = p.get(section, 'abbr')
        if id_ not in provider_map:
            args.log.info('adding provider %s' % slug(id_))
            DBSession.add(
                Provider(id=id_, name=name, description=description, abbr=abbr))


def update_refnames(args):
    for ref in DBSession.query(Ref).order_by(desc(Ref.pk)):
        name = '%s %s' % (ref.author or 'n.a.', ref.year or 'n.d.')
        if name != ref.name:
            args.log.info('%s: %s -> %s' % (ref.id, ref.name, name))
            ref.name = name


if __name__ == '__main__':
    import doctest
    doctest.testmod()
