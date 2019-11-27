import pathlib
import functools
import itertools

from mako.template import Template
import attr
from sqlalchemy import create_engine
from clldutils import jsonlib


T = Template("""\
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Glottolog ${version} - ${lang.text}</title>
        <link href="/clld-static/css/bootstrap.min.css" rel="stylesheet">
        <link href="/clld-static/css/bootstrap-responsive.min.css" rel="stylesheet">
        <link href="/static/project.css" rel="stylesheet">
    </head>
    <body>
        <div class="navbar navbar-static-top navbar-inverse">
            <div class="navbar-inner">
                <div class="container-fluid">
                    <a class="brand active" style="color: white !important" title="Glottolog ${version}">Glottolog ${version}</a>
                </div>
            </div>
        </div>
        <div class="container-fluid">
            <div class="row-fluid" style="margin-top: 10px;">
                <div class="span12">
                    <div class="alert alert-error">
                        You are browsing an outdated version of Glottolog. The current
                        version can be found at
                        <a href="https://glottolog.org">https://glottolog.org</a>.
                    </div>
                </div>
            </div>
            <div class="row-fluid">
                <div class="span8">
                    <h3>${lang.level.capitalize() + ': ' if lang.level else ''}<span class="level-${lang.level}">${lang.name}</span> [${lang.id}]</h3>

                    % if replacements:
                    <div class="alert">
                        This languoid is no longer part of the Glottolog classification.
                        You may want to look at the following languoids for relevant information.
                    </div>
                    <ul>
                        % for r in replacements:
                        <li>${r}</li>
                        % endfor
                    </ul>
                    % endif

                    % if clf:
                    <h4>Classification</h4>
                    ${clf|n}
                    % endif

                    % if identifiers:
                    <h4>Identifiers</h4>
                    <ul>
                        % for i in identifiers:
                        <li>${i}</li>
                        % endfor
                    </ul>
                    % endif
                </div>
                <div class="span4">
                    <div class="well well-small">
                        <h4>Other Versions</h4>
                        <ul>
                            % for v in versions:
                            <li>${v|n}</li>
                            % endfor
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </body>
</html>
""")


def wrap(agg, l):
    return "\n<ul>\n<li>\n{1}\n{0}\n</li>\n</ul>\n".format(agg, l)


def link_list(l):
    return "\n<ul>\n{0}\n</ul>\n".format(
        '\n'.join('<li>{0}</li>'.format(ll.link) for ll in l))


@attr.s
class L:
    pk = attr.ib()
    id = attr.ib()
    name = attr.ib()
    version = attr.ib()
    level = attr.ib(default=None)
    fpk = attr.ib(default=None)
    replacements = attr.ib(default=attr.Factory(list))

    def __str__(self):
        res = '{0.name} [{0.id}]'.format(self)
        if self.level:
            res += ' {0.level}'.format(self)
        if self.replacements:
            res += ' superseded'
        return res

    @property
    def text(self):
        return self.__str__()

    @property
    def link(self):
        return '<a href="{0.id}.html">{0}</a>'.format(self)

    @property
    def cross_version_link(self):
        return '<a href="../glottolog-{0.version}/{0.id}.html">[{0.id}] in Glottolog {0.version}</a>'.format(self)


@attr.s
class I:
    lpk = attr.ib()
    name = attr.ib()
    description = attr.ib()
    type = attr.ib()

    def __str__(self):
        if self.type == 'name':
            return '{0.description} name: {0.name}'.format(self)
        return '{0.type}: {0.name}'.format(self)


def dump(out, version, all_langs, identifiers):
    if out.exists():
        for p in out.iterdir():
            p.unlink()
    else:
        out.mkdir()

    langs = all_langs[version].values()
    langs_by_pk = {l.pk: l for l in langs}

    children = {
        pk: list(c)
        for pk, c in itertools.groupby(sorted(langs, key=lambda l: l.fpk or 0), lambda l: l.fpk)}

    for lang in langs:
        ancestors, fpk = [], lang.fpk
        while fpk and fpk in langs_by_pk:
            ancestors.append(langs_by_pk[fpk])
            fpk = langs_by_pk[fpk].fpk

        versions = [
            '<strong><a href="https://glottolog.org/resource/languoid/id/{0}">[{0}] in current Glottolog</a></strong>'.format(lang.id)]
        for v in sorted(all_langs.keys()):
            if v != version:
                if lang.id in all_langs[v]:
                    versions.append(all_langs[v][lang.id].cross_version_link)
        clf = [link_list(children.get(lang.pk, []))]
        clf.append(lang.text)
        clf.extend(a.link for a in ancestors)
        out.joinpath('{0}.html'.format(lang.id)).write_text(
            T.render_unicode(
                version=version,
                lang=lang,
                clf=functools.reduce(wrap, clf) if not lang.replacements else '',
                versions=versions,
                identifiers=identifiers.get(lang.pk, []),
                replacements=[all_langs[version][lid].link for lid in lang.replacements
                              if lid in all_langs[version]],
                wrap=wrap,
                link_list=link_list,
            ),
            encoding='utf8',
        )


def aggregate(version, langs, identifiers):
    """
    Aggregate language data across database versions.

    This requires a compatible core schema across **all** Glottolog versions >= 2.0!
    The minimal requirements can be gleaned from the SQL queries in this function; almost all
    are implemented in the clld core schema, except a table

    languoid
    - level
    - father_pk

    and optionally a table

    superseded
    - languoid_pk
    - replacement_pk
    """
    db = create_engine('postgresql://postgres@/glottolog-{0}'.format(version))
    langs[version] = {
        r['id']: L(r['pk'], r['id'], r['name'], version, r['level'], r['father_pk'])
        for r in db.execute("""\
SELECT l.pk, l.id, l.name, ll.level, ll.father_pk
FROM language AS l, languoid AS ll WHERE l.pk = ll.pk AND l.active = true""")}

    has_superseded = db.scalar("""\
select exists 
(select 1 from pg_tables where schemaname = 'public' and tablename = 'superseded')""")
    if has_superseded:  # dropped in 3.1
        for r in db.execute("""\
select l.pk, l.id, l.name, string_agg(ll.id, ' ') as replacements
from language as l, language as ll, superseded as s
where l.pk = s.languoid_pk and ll.pk = s.replacement_pk
group by l.pk, l.id, l.name
            """):
            if r['id'] not in langs[version]:
                langs[version][r['id']] = L(
                    r['pk'], r['id'], r['name'], version, replacements=r['replacements'].split())

    identifiers[version] = [
        I(r['language_pk'], r['name'], r['description'], r['type']) for r in
        db.execute("""\
select li.language_pk, i.name, i.description, i.type
from languageidentifier as li, identifier as i
where li.identifier_pk = i.pk order by li.language_pk, i.type, i.description, i.name""")]


def create(versions, out=None):
    out = out or pathlib.Path('archive')
    if not out.exists():
        out.mkdir()

    langs, identifiers = {}, {}
    for version in versions:
        aggregate(version, langs, identifiers)

    for version in versions:
        dump(
            out.joinpath('glottolog-{0}'.format(version)),
            version, 
            langs,
            {pk: list(c) for pk, c in itertools.groupby(identifiers[version], lambda i: i.lpk)})

    gc2v = {}
    for v in versions:
        for gc in sorted(langs[v].keys()):
            gc2v[gc] = v
    jsonlib.dump(gc2v, out.joinpath('glottocode2version.json'), indent=4)
