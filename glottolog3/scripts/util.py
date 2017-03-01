from __future__ import unicode_literals, print_function
import io
import re
from collections import Counter
from itertools import groupby
from six.moves.configparser import RawConfigParser

from sqlalchemy import desc, and_
from sqlalchemy.orm import joinedload_all
from path import path

from clldutils.misc import slug
from clldutils.jsonlib import load as jsonload
from clld.db.meta import DBSession
from clld.lib.bibtex import Database
from clld.db.models.common import Source, Language, LanguageIdentifier, Identifier
from clld.db.util import page_query
from clld.scripts.util import parsed_args, ExistingDir

from glottolog3.lib.util import get_map, roman_to_int
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


def glottolog_name(**kw):
    return Identifier(type='name', description='Glottolog', **kw)


def glottolog_names():
    gl_name = glottolog_name()
    return {i.name: i for i in DBSession.query(Identifier).filter(and_(
        Identifier.type == gl_name.type,
        Identifier.description == gl_name.description))}


def get_args():
    return parsed_args(
        (("--data-dir",),
         dict(
             action=ExistingDir,
             default=path('/home/shh.mpg.de/forkel/venvs/glottolog3/glottolog/'))))


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


def get_codes(ref):
    """detect language codes in a string

    known formats:
    - cul
    - cul, Culina [cul]
    - cul, aka
    - [cul, aka, NOCODE_Culina]
    """
    code_map = {
        'NOCODE_Eviya': 'gev',
        'NOCODE_Ndambomo': 'nxo',
        'NOCODE_Osamayi': 'syx',
    }

    # look at everything in square brackets
    for match in SQUARE_BRACKET_PATTERN.finditer(ref.language_note):
        # then split by comma, and look at the parts
        for code in [s.strip() for s in match.group('content').split(',')]:
            if CODE_PATTERN.match(code):
                yield code_map.get(code, code)


def get_bibkeys(bibrec):
    if 'srctrickle' not in bibrec:
        print(bibrec)
        raise ValueError
    return {provider: [rec[1] for rec in recs] for provider, recs in groupby(
        [t.split('#', 1) for t in sorted(re.split('\s*,\s*', bibrec['srctrickle']))],
        lambda p: p[0])}


def get_bib(args):
    return Database.from_file(args.data_dir.joinpath('scripts', 'monster-utf8.bib'))


def update_reflang(args):
    stats = Counter()

    languoid_map = {}
    for l in DBSession.query(Languoid).options(joinedload_all(
        Language.languageidentifier, LanguageIdentifier.identifier
    )):
        if l.hid:
            languoid_map[l.hid] = l.pk
        elif l.iso_code:
            languoid_map[l.iso_code] = l.pk
        languoid_map[l.id] = l.pk

    lgcodes = {}
    for rec in get_bib(args):
        lgcode = ''
        for f in 'lgcode lcode lgcde lgcoe lgcosw'.split():
            if rec.get(f):
                lgcode = rec[f]
                break
        if len(lgcode) == 3 or lgcode.startswith('NOCODE_'):
            lgcode = '[' + lgcode + ']'
        lgcodes[rec.get('glottolog_ref_id', None)] = lgcode

    for ref in page_query(
            DBSession.query(Ref).order_by(desc(Source.pk)),
            n=10000,
            commit=True,
            verbose=True):
        if ref.id not in lgcodes:
            # remove all language relations for refs no longer in bib!
            update_relationship(ref.languages, [])
            stats.update(['obsolete'])
            continue

        language_note = lgcodes[ref.id]
        trigger = ca_trigger(language_note)
        if trigger:
            ref.ca_language_trigger, ref.language_note = trigger
        else:
            ref.language_note = language_note

        # keep relations to non-language languoids:
        # FIXME: adapt this for bib-entries now referring to glottocodes of
        #        families/dialects (e.g. add a sticky-bit to languagesource)
        langs = [
            l for l in ref.languages if
            (l.level != LanguoidLevel.language or not l.active)]
        langs_pk = [l.pk for l in langs]

        for code in set(get_codes(ref)):
            if code not in languoid_map:
                stats.update([code])
                continue
            lpk = languoid_map[code]
            if lpk not in langs_pk:
                langs.append(DBSession.query(Languoid).get(lpk))
                langs_pk.append(lpk)

        a, r = update_relationship(ref.languages, langs)
        if a or r:
            stats.update(['changed'])

    args.log.info('%s' % stats)


def recreate_treeclosure(session=None):
    """
    Denormalize ancestry, top-level and descendant counts for languoids.

    Recreates treeclosuretable and updates the following attributes of languoids:
    - family_pk
    - child_family_count
    - child_language_count
    - child_dialect_count
    """
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
      COALESCE(l.child_family_count, -1) != u.child_family_count OR
      COALESCE(l.child_language_count, -1) != u.child_language_count OR
      COALESCE(l.child_dialect_count, -1) != u.child_dialect_count)"""]
    for s in sql:
        session.execute(s)
    session.execute('COMMIT')


def update_providers(args, verbose=False):
    filepath = args.data_dir.joinpath('references', 'bibtex', 'BIBFILES.ini')
    p = RawConfigParser()
    with io.open(filepath, encoding='utf-8-sig') as fp:
        p.readfp(fp)

    provider_map = get_map(Provider)
    for section in p.sections():
        sectname = section[:-4] if section.endswith('.bib') else section
        id_ = slug(sectname)
        attrs = {
            'name': p.get(section, 'title'),
            'description': p.get(section, 'description'),
            'abbr': p.get(section, 'abbr'),
        }
        if id_ in provider_map:
            provider = provider_map[id_]
            for a in list(attrs):
                before, after = getattr(provider, a), attrs[a]
                if before == after:
                    del attrs[a]
                else:
                    setattr(provider, a, after)
                    attrs[a] = (before, after)
            if attrs:
                args.log.info('updating provider %s %s' % (slug(id_), sorted(attrs)))
            if verbose:
                for a, (before, after) in attrs.items():
                    before, after = (' '.join(_.split()) for _ in (before, after))
                    if before != after:
                        args.log.info('%s\n%r\n%r' % (a, before, after))
        else:
            args.log.info('adding provider %s' % slug(id_))
            DBSession.add(Provider(id=id_, **attrs))


def update_refnames(args):
    for ref in DBSession.query(Ref).order_by(desc(Ref.pk)):
        name = '%s %s' % (ref.author or 'n.a.', ref.year or 'n.d.')
        if name != ref.name:
            args.log.info('%s: %s -> %s' % (ref.id, ref.name, name))
            ref.name = name


if __name__ == '__main__':
    import doctest
    doctest.testmod()
