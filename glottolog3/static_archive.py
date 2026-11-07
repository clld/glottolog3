import shutil
import pathlib
import functools
import itertools
import subprocess
import collections
import dataclasses

from mako.template import Template
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


@dataclasses.dataclass
class L:
    pk: int
    id: str
    name: str
    version: str
    level: str
    fpk: int

    def __str__(self):
        res = '{0.name} [{0.id}]'.format(self)
        if self.level:
            res += ' {0.level}'.format(self)
        return res

    @property
    def text(self):
        return self.__str__()

    @property
    def link(self):
        return '<a href="{0.id}.html">{0}</a>'.format(self)

    def cross_version_link(self, v):
        return f'<a href="../glottolog-{v}/{self.id}.html">[{self.id}] in Glottolog {v}</a>'


@dataclasses.dataclass
class I:
    lpk: int
    name: str
    description: str
    type: str

    def __str__(self):
        if self.type == 'name':
            return '{0.description} name: {0.name}'.format(self)
        return '{0.type}: {0.name}'.format(self)


def dump(out, version, older, langs, identifiers):
    if out.exists():
        for p in out.iterdir():
            p.unlink()
    else:
        out.mkdir()

    langs = langs.values()
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
            '<strong><a href="https://glottolog.org/resource/languoid/id/{0}">[{0}] in latest version</a></strong>'.format(lang.id)]
        for ov in reversed(older.get(lang.id)):
            if ov != version:
                versions.append(lang.cross_version_link(ov))

        clf = [link_list(children.get(lang.pk, []))]
        clf.append(lang.text)
        clf.extend(a.link for a in ancestors)
        out.joinpath('{0}.html'.format(lang.id)).write_text(
            T.render_unicode(
                version=version,
                lang=lang,
                clf=functools.reduce(wrap, clf),
                versions=versions,
                identifiers=identifiers.get(lang.pk, []),
                wrap=wrap,
                link_list=link_list,
            ),
            encoding='utf8',
        )


def aggregate(version, db):
    """
    Aggregate language data across database versions.

    This requires a compatible core schema across **all** Glottolog versions >= 2.0!
    The minimal requirements can be gleaned from the SQL queries in this function; almost all
    are implemented in the clld core schema, except a table

    languoid
    - level
    - father_pk
    """
    langs = {
        r['id']: L(r['pk'], r['id'], r['name'], version, r['level'], r['father_pk'])
        for r in db.execute("""\
SELECT l.pk, l.id, l.name, ll.level, ll.father_pk
FROM language AS l, languoid AS ll WHERE l.pk = ll.pk AND l.active = true""")}

    identifiers = [
        I(r['language_pk'], r['name'], r['description'], r['type']) for r in
        db.execute("""\
select li.language_pk, i.name, i.description, i.type
from languageidentifier as li, identifier as i
where li.identifier_pk = i.pk order by li.language_pk, i.type, i.description, i.name""")]
    return langs, identifiers


def create(version, older, glottocode2version, out=None):
    out = out or pathlib.Path('.')
    out = out / version
    if not out.exists():
        out.mkdir(exist_ok=True, parents=True)

    langs, identifiers = aggregate(version, create_engine('postgresql://postgres@/glottolog-{0}'.format(version)))
    gc2v = jsonlib.load(glottocode2version)

    subdir = out / f'glottolog-{version}'
    dump(
        subdir,
        version,
        gc2v,
        langs,
        {pk: list(c) for pk, c in itertools.groupby(identifiers, lambda i: i.lpk)})
    subprocess.check_call(['zip', '-r', f'{subdir.name}.zip', subdir.name], cwd=str(out))
    shutil.rmtree(subdir)

    for gc in langs:
        if gc in gc2v:
            if version not in gc2v[gc]:
                gc2v[gc].append(version)
        else:
            gc2v[gc] = [version]
    jsonlib.dump(collections.OrderedDict(
        (gc, gc2v[gc]) for gc in sorted(gc2v)), out.joinpath('glottocode2version.json'), indent=4)
