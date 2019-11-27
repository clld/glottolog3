import json
import pathlib

from clld.db.meta import DBSession
from clld.db.models import common
from clldutils import misc
from clldutils.text import split_text

from glottolog3.models import TreeClosureTable


def split_items(s):  # pragma: no cover
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


def add_identifiers(data, dblang, items, name_type=False):
    for prov, names in items.items():
        if not isinstance(names, (list, tuple)):
            names = split_text(names, separators=',;')
        for name in names:
            lang = 'en'
            if name_type:
                if '[' in name and name.endswith(']'):
                    name, lang = [s.strip() for s in name[:-1].split('[', 1)]
                add_identifier(
                    dblang,
                    data,
                    name,
                    'name' if name_type else prov,
                    prov if name_type else None,
                    lang)


def add_identifier(languoid, data, name, type, description, lang):
    if len(lang) > 3:
        # Weird stuff introduced via hhbib_lgcode names. Roll back language parsing.
        name, lang = '{0} [{1}]'.format(name, lang), 'en'
    identifier = data['Identifier'].get((name, type, description, lang))
    if not identifier:
        identifier = data.add(
            common.Identifier,
            (name, type, description, lang),
            id=idjoin(slug(name, escape=type == 'name'), slug(type), slug(description or ''), lang),
            name=name,
            type=type,
            description=description,
            lang=lang)
    DBSession.add(common.LanguageIdentifier(language=languoid, identifier=identifier))


def read_macroarea_geojson(api, name, desc):
    p = {
        p.stem.replace('_', ''): p
        for p in api.path('config', 'macroareas', 'voronoi').glob('*.geojson')
    }[name.lower().replace(' ', '')]

    with p.open(encoding='utf-8-sig') as fp:
        d = json.load(fp)
        d['properties'] = {
            'label': name,
            'description': '<strong>{0}:</strong> {1}'.format(name, desc)}
        return d


def add_parameter(data, id_, domain=None, name=None, pkw=None, dekw=None, delookup='id'):
    p = data.add(common.Parameter, id_, id=id_, name=name or id_.capitalize(), **pkw or {})
    for de in sorted(domain or []):
        kw = dict(id=idjoin(p.id, de.id), parameter=p)
        if dekw:
            kw.update(dekw(de))
        data.add(common.DomainElement, (p.id, getattr(de, delookup)), **kw)


def add_values(data, dblang, pid, values, with_de=True, **vskw):
    vs = None
    for i, (vid, vname) in enumerate(values):
        if i == 0:
            vs = common.ValueSet(
                id=idjoin(pid, dblang.id),
                language=dblang,
                parameter=data['Parameter'][pid],
                contribution=data['Contribution']['glottolog'],
                **vskw)
        vkw = dict(id=idjoin(pid, slug(vid), dblang.id), name=vname, valueset=vs)
        if with_de:
            vkw['domainelement'] = data['DomainElement'][pid, vid]
        DBSession.add(common.Value(**vkw))


def idjoin(*args):
    if len(args) == 1 and isinstance(args[0], (tuple, list)):
        args = args[0]
    return '-'.join(['{0}'.format(a) for a in args])


def slug(s, escape=False, **kw):
    # That's some weird stuff coming in with ElCat alternative names ...
    return misc.slug(''.join(hex(ord(c)) if escape else c for c in s if ord(c) != 2), **kw)


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
