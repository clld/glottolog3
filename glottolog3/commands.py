# coding: utf8
from __future__ import unicode_literals, print_function, division
from collections import Counter, defaultdict
import re
from itertools import groupby
from subprocess import check_output

from six import text_type
from sqlalchemy import desc
from sqlalchemy.orm import joinedload, joinedload_all
import transaction
from clld.db.meta import DBSession
from clld.db.models.common import (
    Parameter, ValueSet, Value, Contribution, ValueSetReference, LanguageIdentifier,
    Language, Identifier, Source,
)
from clldutils.clilib import command
from clldutils.markup import Table
from clldutils.iso_639_3 import ISO
from clldutils.misc import slug

from glottolog3.models import (
    Languoid, LanguoidLevel, LanguoidStatus, Superseded,
    Languoidcountry, Languoidmacroarea, Macroarea, Country,
)
from glottolog3.scripts.util import recreate_treeclosure

COUNTRY_ID_PATTERN = re.compile('\((?P<id>[A-Z]{2})\)')


# TODO:
# 0. turn superseded.csv into simple replacements -> closest common ancestor of all
# replacements
# NO! simply add to config with Config.gone! 410 is better than 301 - which implies
# sort of equivalent content.
# 1. we need a command to compute additions to superseded.csv before recreating the DB!
# 2. We need a command to compute new refs and new languoids, so that these can be marked
#
# for refs:
# - read new monster
# - compare with refs in DB
# - output obsolete/new
#
# for langs:
# - read new tree
# - compare with langs in DB
# - output obsolete/new
#
# accordingly for the feeds.
@command()
def changes(args):
    new = set()
    refid_pattern = re.compile('\s+glottolog_ref_id\s+=\s+\{(?P<id>[0-9]+)\}')
    for i, line in enumerate(
            args.repos.repos.joinpath('build', 'monster-utf8.bib').open(encoding='utf8')):
        match = refid_pattern.match(line)
        if match:
            id_ = match.group('id')
            if id_ in new:
                print('line {0}: duplicate ref id {1}'.format(i + 1, id_))
            new.add(id_)

    old = {s.id for s in DBSession.query(Source)}
    print('refs:')
    print('{0} obsolete'.format(len(old.difference(new))))
    print('{0} new'.format(len(new.difference(old))))

    new = {l.id for l in args.repos.languoids()}
    # FIXME: The superseded languoids must be (?) imported, too!
    old = {l.id for l in DBSession.query(Language)}
    print('languoids:')
    print('{0} obsolete'.format(len(old.difference(new))))
    print('{0} new'.format(len(new.difference(old))))


def create_languoid(l, pk):
    lang_db = Languoid(
        pk=pk,
        id=l.id,
        name=l.name,
        hid=l.hid,
        level=getattr(LanguoidLevel, l.level.name),
        latitude=l.latitude,
        longitude=l.longitude,
        status=LanguoidStatus.established,
        description=l.cfg['core'].get('comment'),
        jsondata=dict(endangerment=l.endangerment.name)
    )
    DBSession.add(lang_db)
    return lang_db


def update_languoid(ldb,
                    lrepos,
                    changes,
                    langs_db,
                    params,
                    contrib,
                    countries,
                    macroareas,
                    identifier,
                    altnames):
    """
    Update a glottolog3 Languoid according to the data of a pyglottolog Languoid.

    :param ldb: glottolog3.models.Languoid
    :param lrepos: pyglottolog.languoids.Languoid
    :param changes: dict recording changes
    :param langs_db: dict mapping id to Languoids in the DB.
    :param params: dict mapping id to Parameter in the DB.
    :param contrib: Contribution object
    :param countries: dict mapping id to Country in the DB.
    :param macroareas: dict mapping name to Macroarea in the DB.
    :return:
    """
    #
    # core           |                        |       0 |
    #                | glottocode             |  23,151 |
    #                | name                   |  23,151 |
    #                | level                  |  23,151 |
    #                | macroareas             |  18,593 |
    #                | hid                    |   8,341 |
    #                | countries              |   8,276 |
    #                | iso639-3               |   7,862 |
    #                | longitude              |   7,625 |
    #                | latitude               |   7,625 |
    #                | status                 |   2,266 |
    #                | comment                |       1 |
    #
    for attr in ['name', 'hid', 'latitude', 'longitude']:
        vdb, vrepos = getattr(ldb, attr), getattr(lrepos, attr)
        if vdb != vrepos:
            changes[ldb.id][attr] = (vdb, vrepos)

    if lrepos.cfg[lrepos.section_core].get('comment') and \
            ldb.description != lrepos.cfg[lrepos.section_core].get('comment'):
        changes[ldb.id]['comment'] = (
            ldb.description, lrepos.cfg[lrepos.section_core]['comment'])
        ldb.description = lrepos.cfg[lrepos.section_core]['comment']

    if ldb.level.name != lrepos.level.name:
        changes[ldb.id]['level'] = (ldb.level.name, lrepos.level.name)
        ldb.level = getattr(LanguoidLevel, lrepos.level.name)

    for ma in lrepos.macroareas:
        if ma not in macroareas:
            raise ValueError('{0} invalid macroarea: {1}'.format(lrepos.id, ma))
        DBSession.add(Languoidmacroarea(
            languoid_pk=ldb.pk,
            macroarea_pk=macroareas[ma].pk))

    for country in lrepos.cfg.getlist(lrepos.section_core, 'countries'):
        match = COUNTRY_ID_PATTERN.search(country)
        if not match or match.group('id') not in countries:
            raise ValueError('{0} invalid country: {1}'.format(lrepos.id, country))
        DBSession.add(Languoidcountry(
            languoid_pk=ldb.pk,
            country_pk=countries[match.group('id')].pk))

    if lrepos.iso:
        DBSession.add(LanguageIdentifier(
            language=ldb, identifier=identifier[(lrepos.iso, 'iso639-3')]))

    if lrepos.endangerment:
        param = params['vitality']
        for de in param.domain:
            if de.number == lrepos.endangerment.value:
                vid = 'vitality{0}'.format(ldb.pk)
                valueset = ValueSet(
                    id=vid,
                    language=ldb,
                    parameter=param,
                    contribution=contrib)
                _ = Value(
                    id=vid,
                    name=text_type(lrepos.endangerment.name),
                    domainelement=de,
                    valueset=valueset)
                break

    #
    # update classification:
    # - father_pk
    # - family- and subclassification comment
    #
    if lrepos.lineage:
        # FIXME: update ldb.status according to the top-level pseudo-family!
        # maybe some day store lrepos.category?

        new = langs_db[lrepos.lineage[-1][1]]
        if new.pk != ldb.father_pk:
            changes[ldb.id]['classification'] = (
                ldb.father.id if ldb.father else None, new.id)
            ldb.father_pk = new.pk
    else:
        if ldb.father_pk:
            changes[ldb.id]['classification'] = (ldb.father.id, None)
            ldb.father_pk = None

    for id_, attr in [('fc', 'family'), ('sc', 'sub')]:
        comment = getattr(lrepos.classification_comment, attr)
        if comment:
            vid = '{0}{1}'.format(id_, ldb.pk)
            valueset = ValueSet(
                id=vid,
                description=comment,
                language=ldb,
                parameter=params[id_],
                contribution=contrib)
            _ = Value(
                id=vid,
                name='%s - %s' % (ldb.level, ldb.status),
                valueset=valueset)

    #
    # section iso_retirement:
    #
    if lrepos.iso_retirement:
        ldb.update_jsondata(iso_retirement=lrepos.iso_retirement.asdict())
    else:
        if 'iso_retirement' in ldb.jsondata:
            jd = ldb.jsondata.copy()
            del jd['iso_retirement']
            ldb.jsondata = jd

    #
    # section identifier:
    #
    ipk = DBSession.query(Identifier.pk).order_by(desc(Identifier.pk)).first()[0]
    for type_, ids in lrepos.identifier.items():
        for id_ in ids.split(';'):
            if (id_, type_) not in identifier:
                raise ValueError('{0} unknown identifier: {1} {2}'.format(ldb.id, id_, type_))
            DBSession.add(LanguageIdentifier(
                language=ldb, identifier=identifier[(id_, type_)]))

    #
    # section altnanmes:
    #
    for type_, names in lrepos.names.items():
        for name in names:
            id_ = altnames.get((name, type_))
            if not id_:
                ipk += 1
                id_ = Identifier(
                    type='name', description=type_, name=name, pk=ipk, id='%s' % ipk)
                print('{0} unknown name: {1} {2}'.format(ldb.id, name, type_))
            DBSession.add(LanguageIdentifier(language=ldb, identifier=id_))

    return ldb.id in changes


@command()
def update_tree(args):
    langs_repos = {l.id: l for l in args.repos.languoids()}
    codes_repos = set(langs_repos.keys())
    assert langs_repos

    with transaction.manager:
        langs_db = {l.id: l for l in DBSession.query(Languoid)}
        codes_db = set(langs_db.keys())

        # make sure no inactive languoids have crept back into the repository:
        assert not codes_repos.intersection(
            [l.id for l in langs_db.values() if not l.active])

        stats, updates, changes = defaultdict(set), Counter(), defaultdict(dict)

        hids = {l.hid: l for l in langs_db.values() if l.hid}
        for l in langs_repos.values():
            if l.hid and l.hid in hids and hids[l.hid].id != l.id:
                print('---resetting hid {0}: {1}'.format(l.hid, hids[l.hid]))
                hids[l.hid].hid = None
        DBSession.flush()

        maxpk = max([l.pk for l in langs_db.values()])

        for code in codes_repos.difference(codes_db):
            maxpk += 1
            stats['new'].add(code)
            l = create_languoid(langs_repos[code], maxpk)
            langs_db[l.id] = l
            codes_db.add(l.id)

        DBSession.flush()
        assert not codes_repos.difference(codes_db)

        cc = {
            p.id: p for p in DBSession.query(Parameter)
            .filter(Parameter.id.in_(['fc', 'sc', 'vitality']))
            .options(joinedload(Parameter.domain))}
        DBSession.query(Value).delete()
        DBSession.query(ValueSetReference).delete()
        DBSession.query(ValueSet).delete()
        DBSession.query(Languoidmacroarea).delete()
        DBSession.query(Languoidcountry).delete()
        DBSession.query(LanguageIdentifier).delete()
        contrib = Contribution.first()

        countries = {c.id: c for c in DBSession.query(Country)}
        macroareas = {c.name: c for c in DBSession.query(Macroarea)}
        identifier = {(i.name, i.type): i for i in
                      DBSession.query(Identifier).filter(Identifier.type != 'name')}
        altnames = {('{0} [{1}]'.format(i.name, i.lang) if i.description == 'lexvo'
                     else i.name, i.description.lower()): i for i in
                    DBSession.query(Identifier).filter(Identifier.type == 'name')}

        for code in codes_db.intersection(codes_repos):
            if update_languoid(
                langs_db[code],
                langs_repos[code],
                changes,
                langs_db,
                cc,
                contrib,
                countries,
                macroareas,
                identifier,
                altnames,
            ):
                updates.update(changes[code].keys())
                if code not in stats['new']:
                    stats['update'].add(code)
        print(updates)
        for p in cc.values():
            print('{0}: {1}'.format(p.id, len(p.valuesets)))

        for code in codes_db.difference(codes_repos):
            lang = langs_db[code]
            if not lang.active:
                # ignore whatever is already inactive
                continue

            # Relate obsolete families with their closest counterpart
            # -> just compute closest sub-group above, which is still present!
            for i, ancestor in enumerate(lang.get_ancestors()):
                if ancestor.id in codes_repos:
                    DBSession.add(Superseded(
                        languoid_pk=lang.pk,
                        replacement_pk=ancestor.pk,
                        relation='classification update'))
                    break
            else:
                print('== no replacement == {0}'.format(code))

            lang.active = False
            lang.father_pk = None
            #
            # unlink children!
            #
            stats['obsolete'].add(lang.id)

        print('new: {0}; updated: {1}; obsolete: {2}'.format(
            len(stats['new']),
            len(stats['update']),
            len(stats['obsolete'])))

        DBSession.flush()
        recreate_treeclosure()
        # TODO:
        # fill in legacy codes according to languoids/glottocodes.json
        raise ValueError


@command()
def jsondata(args):
    ops = defaultdict(Counter)

    for l in DBSession.query(Languoid):
        for sec in l.jsondata:
            if isinstance(l.jsondata[sec], dict):
                for opt in l.jsondata[sec]:
                    ops[sec].update([opt])
            else:
                ops[sec].update(['-'])

    t = Table('key', 'sub-key', 'count')
    for section, options in ops.items():
        t.append([section, '', 0.0])
        for k, n in options.most_common():
            t.append(['', k, float(n)])
    print(t.render(condensed=False, floatfmt=',.0f'))


ckm = {
    "hh:h:ClouseDonohueMa:NCoast": "hh:hld:ClouseDonohueMa:NCoast",
    "hh:ld:Goddard:Mahican": "hh:phonvld:Goddard:Mahican",
    "hh:hv:Labroussi:Sud-Ouest-Tanzania": "hh:hv:Labroussi:Sud-Ouest-Tanzanie",
    "hh:s:Shackle:Hindko": "hh:hv:Shackle:Hindko",
    "hh:hwb:Bokula:Irumu:Moru-Mangbetu": None,
    "hh:g:Kattenbusch:Frankoprovenzalische": "hh:gtd:Kattenbusch:Frankoprovenzalische",
    "hh:h:SkarGurung:Tharus": None,
    "hh:hv:Reesink:Aramia": "hh:hvw:Reesink:Aramia",
    "hh:dialsoc:Berndt:Western-Desert": "hh:h:Berndt:Western-Desert",
    "hh:g:Varma:Bhalesi": "hh:s:Varma:Bhalesi",
    "hh:vphon:BodtLieberherr:Bangru": "hh:vwphon:BodtLieberherr:Bangru",
}


@command()
def vs(args):
    from clldutils.dsv import reader

    def citekey(srctrickle):
        for key in srctrickle.split(','):
            key = key.strip()
            if key.startswith('hh#'):
                return ckm.get(key.replace('#', ':'), key.replace('#', ':'))

    keys = set()
    with args.repos.repos.joinpath('references', 'bibtex', 'hh.bib').open(encoding='utf8') as fp:
        for line in fp:
            if line.startswith('@'):
                keys.add('hh:' + line.split('{')[1].split(',')[0].strip())

    for row in reader('valuesetrefs.csv', namedtuples=True):
        if citekey(row.srctrickle) not in keys:
            print('    "{0}": "",'.format(citekey(row.srctrickle)))

    refs = defaultdict(dict)
    for spec, rows in groupby(
        sorted(reader('valuesetrefs.csv', namedtuples=True), key=lambda r: (r.glottocode, r.parameter)),
        lambda rr: (rr.glottocode, rr.parameter)
    ):
        refs[spec[0]][spec[1]] = [(r.refname, citekey(r.srctrickle), r.description, r.refid) for r in rows if citekey(r.srctrickle)]

    for l in args.repos.languoids():
        if l.id in refs:
            if 'classification' not in l.cfg:
                l.cfg['classification'] = {}
            fc = refs[l.id].get('fc')
            sc = refs[l.id].get('sc')
            if fc:
                l.cfg.set('classification', 'familyrefs', ['{0} [{2}] ({3} {1})'.format(*t) for t in fc])
            if sc:
                l.cfg.set('classification', 'subrefs', ['{0} [{2}] ({3} {1})'.format(*t) for t in sc])
            l.write_info(outdir=l.dir)


@command()
def update_identifier(args):
    """
    Run once, than cleanup and then run whenever ISO or WALS changes!
    """
    wals = {}
    for t in ['language', 'genus', 'family']:
        prefix = '' if t == 'language' else (t + '/')
        wals[t] = {
            prefix + code for code in check_output(
            'psql -d wals3 -c"select id from {0}" -t'.format(t), shell=True
        ).strip().split()}

    iso_tables = list(args.repos.repos.joinpath('iso639-3').glob('*.zip'))
    iso = ISO(iso_tables[0])
    maxid = DBSession.query(Identifier.pk).order_by(desc(Identifier.pk)).first()[0]

    def delete(id_):
        for li in DBSession.query(LanguageIdentifier) \
            .filter(LanguageIdentifier.identifier_pk == id_.pk):
            DBSession.delete(li)
        DBSession.delete(id_)

    def add(name, type_, maxid):
        maxid += 1
        DBSession.add(
            Identifier(pk=maxid, id='%s' % maxid, name=name, type=type_))
        return maxid

    with transaction.manager:
        ingl = defaultdict(dict)
        for i in DBSession.query(Identifier).filter(Identifier.type == 'WALSGenus'):
            i.type = 'wals'
            i.name = 'genus/' + slug(i.name)
            ingl['genus'][i.name] = i

        for i in DBSession.query(Identifier).filter(Identifier.type == 'WALSFamily'):
            i.type = 'wals'
            i.name = 'family/' + slug(i.name)
            ingl['family'][i.name] = i

        for i in DBSession.query(Identifier).filter(Identifier.type == 'WALS'):
            i.type = 'wals'
            ingl['language'][i.name] = i

        for i in DBSession.query(Identifier).filter(Identifier.type == 'wals'):
            i.name = '/'.join([slug(n) for n in i.name.split('/')])
            if '/' in i.name:
                ingl[i.name.split('/')[0]][i.name] = i
            else:
                ingl['language'][i.name] = i

        for t in ['language', 'genus', 'family']:
            missing = wals[t].difference(ingl[t].keys())
            invalid = set(ingl[t].keys()).difference(wals[t])
            if missing:
                print('{0}/{1} WALS {2} codes not in DB'.format(
                    len(missing), len(wals[t]), t))
                for code in missing:
                    maxid = add(code, 'wals', maxid)
            if invalid:
                print('Invalid WALS {0} codes in DB: {1}'.format(t, len(invalid)))
                for code in invalid:
                    delete(ingl[t][code])

        ingl = {l.name: l for l in
                DBSession.query(Identifier).filter(Identifier.type == 'iso639-3')}
        missing = set(iso.keys()).difference(ingl.keys())
        if missing:
            print('{0}/{1} ISO codes not in DB'.format(len(missing), len(iso)))
        invalid = set(ingl.keys()).difference(iso.keys())
        if invalid:
            print('Invalid ISO codes in DB: {0}'.format(invalid))

        for code in invalid:
            delete(ingl[code])

        for code in missing:
            maxid = add(code, 'iso639-3', maxid)
