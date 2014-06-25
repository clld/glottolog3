import re
import json

from sqlalchemy import sql, desc, not_, or_

from clld.db.meta import DBSession
from clld.util import slug
from clld.lib.bibtex import Database
from clld.db.models.common import Source
from clld.db.util import page_query

from glottolog3.lib.util import get_map
from glottolog3.lib.bibtex import unescape
from glottolog3.models import Ref, Languoid, TreeClosureTable, Provider, LanguoidLevel


WORD_PATTERN = re.compile('[a-z]+')
SQUARE_BRACKET_PATTERN = re.compile('\[(?P<content>[^\]]+)\]')
CODE_PATTERN = re.compile('(?P<code>[a-z]{3}|NOCODE_\w+)$')
PAGES_PATTERN = re.compile('(?P<start>[0-9]+)\s*\-\-?\s*(?P<end>[0-9]+)')


def compute_pages(pages):
    start = None
    end = None
    number = None
    match = None

    for match in PAGES_PATTERN.finditer(pages):
        s_start, s_end = match.group('start'), match.group('end')
        if len(s_end) < len(s_start):
            # the case 516-32:
            s_end = s_start[:-len(s_end)] + s_end
        if int(s_end) < int(s_start):
            # the case 532-516:
            s_end, s_start = s_start, s_end
        if start is None:
            start = int(s_start)
        end = int(s_end)
        number = (number or 0) + (end - int(s_start) + 1)

    if not match:
        try:
            start = int(pages)
        except ValueError:
            pass

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
    refs = []
    known_ids = {}
    bib = Database.from_file(args.data_file(args.version, 'refs.bib'), encoding='utf8')
    for rec in bib:
        known_ids[rec['glottolog_ref_id']] = 1

    for row in DBSession.query(Ref.id):
        if row[0] not in known_ids:
            refs.append(row[0])

    with open(args.data_file(args.version, 'obsolete_refs.json'), 'w') as fp:
        json.dump(refs, fp)

    return bib


def match_obsolete_refs(args):
    with open(args.data_file(args.version, 'obsolete_refs.json')) as fp:
        refs = json.load(fp)
    matched = args.data_file(args.version, 'obsolete_refs_matched.json')
    if matched.exists():
        with open(matched) as fp:
            matched = json.load(fp)
    else:
        matched = {}

    #
    # TODO: optionally re-evaluate known-unmatched refs!
    #

    count = 0
    f, m = 0, 0
    for id_ in refs:
        if id_ in matched:
            continue
        count += 1
        if count > 1000:
            print '1000 obsolete refs processed!'
            break
        ref = Ref.get(id_)
        found = False
        if ref.description and len(ref.description) > 5:
            for match in DBSession.query(Ref)\
                    .filter(not_(Source.id.in_(refs)))\
                    .filter(Source.description.contains(ref.description))\
                    .filter(or_(Source.author == ref.author, Source.year == ref.year))\
                    .limit(10):
                print '++', ref.id, '->', match.id, '++', ref.author, '->', match.author, '++', ref.year, '->', match.year
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
                            print '++', ref.id, '->', match.id, '++', ref.description, '->', match.description
                            matched[ref.id] = match.id
                            found = True
                            break
                    except AssertionError:
                        continue
        if not found:
            m += 1
            print '--', ref.id, ref.name, ref.description
            matched[ref.id] = None
        else:
            f += 1
    print f, 'found'
    print m, 'missed'

    with open(args.data_file(args.version, 'obsolete_refs_matched.json'), 'w') as fp:
        json.dump(matched, fp)


def get_lgcodes(ref):
    """detect language codes in a string

    known formats:
    - cul
    - cul, Culina [cul]
    - cul, aka
    - [cul, aka, NOCODE_Culina]
    """
    res = []
    lgcode = ref.jsondatadict.get('lgcode', '')
    if not lgcode:
        return res

    if '[' not in lgcode:
        lgcode = '[%s]' % lgcode

    # look at everything in square brackets
    for match in SQUARE_BRACKET_PATTERN.finditer(lgcode):
        # then split by comma, and look at the parts
        for code in [s.strip() for s in match.group('content').split(',')]:
            if CODE_PATTERN.match(code):
                res.append(code)
    return set(res)


def update_reflang(args):
    changes = {}
    get_obsolete_refs(args)
    with open(args.data_file(args.version, 'obsolete_refs.json')) as fp:
        obsolete_refs = {k: 1 for k in json.load(fp)}

    with open(args.data_file('brugmann_noderefs.json')) as fp:
        brugmann_noderefs = json.load(fp)

    added, removed, unknown = 0, 0, {}
    languoid_map = {}
    for l in DBSession.query(Languoid).filter(Languoid.hid != None):
        languoid_map[l.hid] = l
        languoid_map[l.pk] = l

    for ref in page_query(DBSession.query(Ref).order_by(Source.pk), verbose=True):
        if ref.id in obsolete_refs:
            # remove all language relations!
            ref.update_jsondata(lgcode='')
        # keep relations to non-language languoids:
        remove = brugmann_noderefs['delete'].get(str(ref.pk), [])
        langs = [
            l for l in ref.languages if
            (l.level != LanguoidLevel.language or not l.active) and l.pk not in remove]
        langs_pk = [l.pk for l in langs]
        for lpk in brugmann_noderefs['create'].get(str(ref.pk), []):
            if lpk not in langs_pk:
                l = languoid_map.get(lpk, Languoid.get(lpk, default=None))
                if l:
                    #print 'relation added according to brugmann data'
                    langs.append(l)
                else:
                    print 'brugmann relation for non-existing languoid'

        for code in get_lgcodes(ref):
            if code not in languoid_map:
                unknown[code] = 1
            else:
                l = languoid_map[code]
                if l.pk not in remove:
                    langs.append(l)
                else:
                    print ref.name, ref.id, '--', l.name, l.id
                    print 'relation removed according to brugmann data'

        a, r = update_relationship(ref.languages, langs)
        if a or r:
            changes[ref.id] = ([l.id for l in ref.languages], [l.id for l in langs])
        added += a
        removed += r

    with open(args.data_file(args.version, 'reflang_changes.json'), 'w') as fp:
        json.dump(changes, fp)

    print added, 'added'
    print removed, 'removed'
    print 'unknown codes', unknown.keys()


def recreate_treeclosure():
    DBSession.execute('delete from treeclosuretable')
    SQL = TreeClosureTable.__table__.insert()
    ltable = Languoid.__table__

    # we compute the ancestry for each single languoid
    for lid, fid in DBSession.execute('select pk, father_pk from languoid').fetchall():
        depth = 0
        DBSession.execute(SQL, dict(child_pk=lid, parent_pk=lid, depth=depth))
        tlf = None

        # now follow up the line of ancestors
        while fid:
            tlf = fid
            depth += 1
            DBSession.execute(SQL, dict(child_pk=lid, parent_pk=fid, depth=depth))
            fid = DBSession.execute(
                sql.select([ltable.c.father_pk]).where(ltable.c.pk == fid)
            ).fetchone()[0]

        DBSession.execute(
            'UPDATE languoid SET family_pk = :tlf WHERE pk = :lid', locals())

    # we also pre-compute counts of descendants for each languoid:
    for level in ['language', 'dialect', 'family']:
        DBSession.execute("""\
UPDATE languoid SET child_%(level)s_count = (
    SELECT count(*)
    FROM treeclosuretable as t, languoid as l
    WHERE languoid.pk = t.parent_pk
    AND languoid.pk != t.child_pk AND t.child_pk = l.pk AND l.level = '%(level)s'
)""" % locals())

    DBSession.execute('COMMIT')


def update_providers(args):
    if not args.data_file(args.version, 'provider.txt').exists():
        return

    with open(args.data_file(args.version, 'provider.txt')) as fp:
        content = fp.read().decode('latin1')

    if '\r\n' in content:
        content = content.replace('\r\n', '\n')

    provider_map = get_map(Provider)
    for block in content.split('\n\n\n\n'):
        lines = block.split('\n')
        id_, abbr = lines[0].strip().split(':')
        id_ = id_.split('.')[0]
        description = unescape('\n'.join(lines[1:]))
        name = description.split('.')[0]

        if id_ == 'hedvig-tirailleur':
            id_ = u'skirgard'

        if slug(id_) not in provider_map:
            args.log.info('adding provider %s' % slug(id_))
            DBSession.add(
                Provider(id=slug(id_), name=name, description=description, abbr=abbr))


def update_refnames(args):
    for ref in DBSession.query(Ref).order_by(desc(Ref.pk)):
        name = '%s %s' % (ref.author or 'n.a.', ref.year or 'n.d.')
        if name != ref.name:
            args.log.info('%s: %s -> %s' % (ref.id, ref.name, name))
            ref.name = name
