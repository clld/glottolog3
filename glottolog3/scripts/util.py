import re

from sqlalchemy import sql, desc

from clld.db.meta import DBSession
from clld.util import slug
from clld.lib import dsv
from clld.db.models.common import (
    Parameter, ValueSet, ValueSetReference, Value, Contribution, Source, Language,
)

from glottolog3.lib.util import get_map, REF_PATTERN, PAGES_PATTERN
from glottolog3.lib.bibtex import unescape
from glottolog3.models import (
    Ref, Languoid, TreeClosureTable, Provider, LanguoidLevel, Macroarea,
)


WORD_PATTERN = re.compile('[a-z]+')


def update_relationship(col, new, log=None):
    old = set(item for item in col)
    new = set(new)
    for item in old - new:
        col.remove(item)
        if log:
            log.info('--')
    for item in new - old:
        col.append(item)
        if log:
            log.info('++')


def update_justifications(args):
    """
    - text goes into ValueSet.description
    - refs go into ValueSetReference objects
    """
    def normalized_pages(s):
        match = PAGES_PATTERN.match(s or '')
        if match:
            return match.group('pages')

    #
    # create mappings to look up glottolog languoids matching names in justification files
    #
    langs_by_hid = {}
    langs_by_hname = {}
    langs_by_name = {}

    with transaction.manager:
        for l in DBSession.query(Languoid).filter(Languoid.active == False):
            langs_by_hname[l.jsondatadict.get('hname')] = l
            langs_by_hid[l.hid] = l
            langs_by_name[l.name] = l

        for l in DBSession.query(Languoid).filter(Languoid.active == True):
            langs_by_hname[l.jsondatadict.get('hname')] = l
            langs_by_hid[l.hid] = l
            langs_by_name[l.name] = l

        for id_, type_ in [('fc', 'family'), ('sc', 'subclassification')]:
            for i, row in enumerate(dsv.rows(args.data_file(args.version, '%s_justifications.tab' % type_))):
                name = row[0].decode('utf8')
                name = name.replace('_', ' ') if not name.startswith('NOCODE') else name
                l = langs_by_hname.get(name, langs_by_hid.get(name, langs_by_name.get(name)))
                if not l:
                    raise ValueError(name)

                _r = 3 if type_ == 'family' else 2
                comment = (row[_r].decode('utf8').strip() or None) if len(row) > _r else None
                if comment and not WORD_PATTERN.search(comment):
                    comment = None

                #
                # TODO: look for [NOCODE_ppp] patterns as well!?
                #

                refs = [(int(m.group('id')), normalized_pages(m.group('comment')))
                        for m in REF_PATTERN.finditer(row[2])]

                vs = None
                for _vs in l.valuesets:
                    if _vs.parameter.id == id_:
                        vs = _vs
                        break

                if not vs:
                    args.log.info('%s %s ++' % (l.id, type_))
                    vs = ValueSet(
                        id='%s%s' % (type_, l.id),
                        description=comment,
                        language=l,
                        parameter=Parameter.get(id_),
                        contribution=Contribution.first())
                    DBSession.add(Value(
                        id='%s%s' % (type_, l.id),
                        name='%s - %s' % (l.level, l.status),
                        valueset=vs))
                    DBSession.flush()
                else:
                    if vs.description != comment:
                        args.log.info('%s %s ~~ description' % (l.id, type_))
                        vs.description = comment

                for r in vs.references:
                    DBSession.delete(r)

                for r, pages in refs:
                        vs.references.append(ValueSetReference(
                            source=Source.get(str(r)),
                            description=pages))

            args.log.info('%s %s' % (i, type_))


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


def update_macroareas(args):
    hlang_to_ma = dict(list(dsv.rows(args.data_file(args.version, 'macroareas.tab'))))
    ma_map = get_map(Macroarea)

    # we store references to languages to make computation of cumulated macroareas for
    # families easier
    lang_map = {}

    for language in DBSession.query(Languoid)\
            .filter(Language.active == True)\
            .filter(Languoid.hid != None):
        lang_map[language.pk] = language

        if language.hid in hlang_to_ma:
            update_relationship(
                language.macroareas,
                [ma_map[hlang_to_ma[language.hid]]],
                log=args.log)

    for family in DBSession.query(Languoid)\
            .filter(Languoid.level == LanguoidLevel.family)\
            .filter(Language.active == True):
        mas = []
        for lang in DBSession.query(TreeClosureTable.child_pk)\
                .filter(TreeClosureTable.parent_pk == family.pk):
            if lang[0] in lang_map:
                mas.extend(lang_map[lang[0]].macroareas)
        update_relationship(family.macroareas, mas, log=args.log)


def update_coordinates(args):
    diff = lambda x, y: abs(x - y) > 0.001

    hlang_to_coord = {
        row[0]: (float(row[1]), float(row[2]))
        for row in dsv.rows(args.data_file(args.version, 'coordinates.tab'))}

    for language in DBSession.query(Languoid)\
            .filter(Language.active == True)\
            .filter(Languoid.hid != None):
        if language.hid in hlang_to_coord:
            lon, lat = hlang_to_coord[language.hid]
            if not language.latitude or not language.longitude:
                language.longitude, language.latitude = lon, lat
                args.log.info('++ %s' % language.id)
            elif diff(language.longitude, lon) or diff(language.latitude, lat):
                language.longitude, language.latitude = lon, lat
                args.log.info('~~ %s' % language.id)


def update_refnames(args):
    for ref in DBSession.query(Ref).order_by(desc(Ref.pk)):
        name = '%s %s' % (ref.author or 'n.a.', ref.year or 'n.d.')
        if name != ref.name:
            args.log.info('%s: %s -> %s' % (ref.id, ref.name, name))
            ref.name = name
