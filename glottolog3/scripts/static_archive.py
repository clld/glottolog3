from __future__ import unicode_literals
from itertools import groupby

from mako.template import Template
import attr
from sqlalchemy import create_engine
from clldutils.path import write_text, remove
from clldutils.misc import UnicodeMixin
from clldutils import jsonlib
from clld.scripts.util import parsed_args


T = Template("""\
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Glottolog ${version} - ${lang.text}</title>
    </head>
    <body>
        <h1>Glottolog ${version}</h1>
        <h2>${lang.text}</h2>

        <h3>Classification</h3>
        ${clf|n}

        % if identifiers:
        <h3>Identifiers</h3>
        <ul>
            % for i in identifiers:
            <li>${i}</li>
            % endfor
        </ul>
        % endif

        <h3>Other Versions</h3>
        <ul>
            % for v in versions:
            <li>${v|n}</li>
            % endfor
        </ul>
    </body>
</html>
""")


def wrap(agg, l):
    return "\n<ul>\n<li>\n{1}\n{0}\n</li>\n</ul>\n".format(agg, l)


def link_list(l):
    return "\n<ul>\n{0}\n</ul>\n".format(
        '\n'.join('<li>{0}</li>'.format(ll.link) for ll in l))


@attr.s
class L(UnicodeMixin):
    pk = attr.ib()
    id = attr.ib()
    name = attr.ib()
    level = attr.ib()
    fpk = attr.ib()
    version = attr.ib()

    def __unicode__(self):
        return '{0.name} [{0.id}] {0.level}'.format(self)

    @property
    def text(self):
        return self.__unicode__()

    @property
    def link(self):
        return '<a href="{0.id}.html">{0}</a>'.format(self)

    @property
    def cross_version_link(self):
        return '<a href="../glottolog-{0.version}/{0.id}.html">{0} in Glottolog {0.version}</a>'.format(self)


@attr.s
class I(UnicodeMixin):
    lpk = attr.ib()
    name = attr.ib()
    description = attr.ib()
    type = attr.ib()

    def __unicode__(self):
        if self.type == 'name':
            return '{0.description} name: {0.name}'.format(self)
        return '{0.type}: {0.name}'.format(self)


def dump(version, all_langs, identifiers):
    out = args.data_file('files', 'glottolog-{0}'.format(version))
    if out.exists():
        for p in out.iterdir():
            remove(p)
    else:
        out.mkdir()

    langs = all_langs[version].values()
    langs_by_pk = {l.pk: l for l in langs}

    children = {pk: list(c) for pk, c in groupby(sorted(langs, key=lambda l: l.fpk), lambda l: l.fpk)}

    for lang in langs:
        ancestors, fpk = [], lang.fpk
        while fpk and fpk in langs_by_pk:
            ancestors.append(langs_by_pk[fpk])
            fpk = langs_by_pk[fpk].fpk

        versions = [
            '<strong><a href="http://glottolog.org/resource/languoid/id/{0}">[{0}] in current Glottolog</a></strong>'.format(lang.id)]
        for v in sorted(all_langs.keys()):
            if v != version:
                if lang.id in all_langs[v]:
                    versions.append(all_langs[v][lang.id].cross_version_link)
        clf = [link_list(children.get(lang.pk, []))]
        clf.append(lang.text)
        clf.extend(a.link for a in ancestors)
        write_text(
            out.joinpath('{0}.html'.format(lang.id)),
            T.render_unicode(
                version=version,
                lang=lang,
                clf=reduce(wrap, clf),
                versions=versions,
                identifiers=identifiers.get(lang.pk, []),
                wrap=wrap,
                link_list=link_list,
            )
        )


if __name__ == '__main__':
    args = parsed_args()
    versions = ['2.0', '2.1', '2.2', '2.3', '2.4', '2.5', '2.6', '2.7']
    langs, identifiers = {}, {}
    for version in versions:
        db = create_engine('postgresql://robert@/glottolog-{0}'.format(version))
        langs[version] = {
            r['id']: L(r['pk'], r['id'], r['name'], r['level'], r['father_pk'], version)
            for r in db.execute("""\
select l.pk, l.id, l.name, ll.level, ll.father_pk
from language as l, languoid as ll where l.pk = ll.pk and l.active = true""")}
        identifiers[version] = [
            I(r['language_pk'], r['name'], r['description'], r['type']) for r in
            db.execute("""\
select li.language_pk, i.name, i.description, i.type
from languageidentifier as li, identifier as i
where li.identifier_pk = i.pk order by li.language_pk, i.type, i.description, i.name""")]

    for version in versions:
        dump(
            version, 
            langs,
            {pk: list(c) for pk, c in groupby(identifiers[version], lambda i: i.lpk)})

    gc2v = {}
    for v in versions:
        for gc in sorted(langs[v].keys()):
            gc2v[gc] = v
    jsonlib.dump(gc2v, args.data_file('glottocode2version.json'), indent=4)
