# coding=utf8
import datetime
import logging
log = logging.getLogger('glottolog3')
import json

import transaction
from sqlalchemy import create_engine
from sqlalchemy import sql
from path import path

from clld.scripts.util import initializedb, Data
from clld.db.meta import DBSession
from clld.db.models import common
from clld.util import slug
from clld.lib import dsv
from clld.lib.bibtex import EntryType

from glottolog3 import models as models2
from glottolog2.lib.util import glottocode, REF_PATTERN


LIMIT = 10000


def select(db, sql, handler):
    offset = 0
    sql += ' limit %s offset %%s' % LIMIT
    log.info(sql)
    batch = db.execute(sql % offset).fetchall()
    while batch:
        handler(offset, batch)
        offset += LIMIT
        log.info('%s' % offset)
        batch = db.execute(sql % offset).fetchall()


def insert(db, table, model, value, start=0, order=None):
    log.info('migrating %s ...' % table)
    sql = 'select * from %s' % table
    values = []
    if not order:
        log.info(sql)
        values = [value(start + i + 1, row) for i, row in enumerate(db.execute(sql))]
        DBSession.execute(model.__table__.insert(), values)
    else:
        def handler(offset, batch):
            _values = [value(start + offset + i + 1, row) for i, row in enumerate(batch)]
            DBSession.execute(model.__table__.insert(), _values)
            values.extend(_values)

        order = [order] if isinstance(order, basestring) else order
        select(db, '%s order by %s' % (sql, ', '.join(order)), handler)

    DBSession.execute('COMMIT')
    log.info('... done')
    return values


def create(args):
    args.log.info('starting migration ...')
    data = Data()
    db = create_engine('postgresql://robert@/glottolog2')

    with transaction.manager:
        sn = data.add(common.Contributor, 'sn', id='sn', name='Sebastian Nordhoff')
        hh = data.add(common.Contributor, 'hh', id='hh', name='Harald Hammarström')
        rf = data.add(common.Contributor, 'rf', id='rf', name='Robert Forkel', url="https://github.com/xrotwang")
        mh = data.add(common.Contributor, 'mh', id='mh', name='Martin Haspelmath')
        contrib = data.add(common.Contribution, 'c', id='classification', name='Classification')
        data.add(common.ContributionContributor, 'hh', contribution=contrib, contributor=hh)
        params = dict(
            fc=data.add(common.Parameter, 'fc', id='fc', name='Family classification'),
            sc=data.add(common.Parameter, 'sc', id='sc', name='Subclassification'),
        )

        dataset = data.add(
            common.Dataset, 'd',
            id='glottolog',
            name='Glottolog 2.0',
            description='',
            published=datetime.date(2013, 8, 15),
            domain='glottolog.org',
            contact='glottolog@eva.mpg.de',
            jsondata={
                'license_icon': 'http://i.creativecommons.org/l/by-sa/3.0/88x31.png',
                'license_name':
                    'Creative Commons Attribution-ShareAlike 3.0 Unported License'})
        for i, ed in enumerate([sn, hh, rf, mh]):
            DBSession.add(common.Editor(dataset=dataset, contributor=ed, ord=i + 1))

        valuesets = {}

        def create_languoid(row, father_pk=None):
            attrs = dict(
                pk=row['id'],
                id=row['alnumcode'],
                name=row['primaryname'],
                description=row['globalclassificationcomment'],
                level=getattr(models2.LanguoidLevel, row['level']),
                status=getattr(models2.LanguoidStatus, (row['status'] or '').replace(' ', '_'), None),
                father_pk=father_pk,
                created=row['updated'],
                jsondata={} if not row['hname'] else {'hname': row['hname']},
            )
            for attr in [
                'active',
                'updated',
                'hid',
                'latitude',
                'longitude',
            ]:
                attrs[attr] = row[attr]
            l = data.add(models2.Languoid, row['id'], **attrs)
            for type_ in params:
                id_ = '%s%s' % (type_, row['id'])
                vs = data.add(
                    common.ValueSet, id_,
                    id=id_,
                    description=row['classificationcomment'] if type_ == 'fc' else row['subclassificationcomment'],
                    language=l,
                    parameter=params[type_],
                    contribution=contrib)
                data.add(common.Value, id_, id=id_, name='%s - %s' % (row['level'], row['status']), valueset=vs)
                DBSession.flush()
                valuesets[id_] = vs.pk
            return str(row['id'])

        level = 0
        parents = [create_languoid(row) for row
                   in db.execute('select * from languoidbase where father_id is null')]
        while parents:
            args.log.info('level: %s' % level)
            level += 1
            parents = [
                create_languoid(row, father_pk=data['Languoid'][row['father_id']].pk)
                for row in db.execute(
                    'select * from languoidbase where father_id in (%s)'
                    % ','.join(parents))]

    def handler(offset, batch):
        svalues = []
        rvalues = []
        for row in batch:
            jsondata = json.loads(row['jsondata'] or "{}")
            jsondata['bibtexkey'] = row['bibtexkey']
            dicts = {
                's': dict(
                    pk=row['id'],
                    polymorphic_type='base',
                    id=str(row['id']),
                    name='%(author)s %(year)s' % row,
                    description=row['title'],
                    bibtex_type=getattr(EntryType, row['type']),
                    jsondata=jsondata),
                'r': dict(pk=row['id']),
            }
            for model, map_ in {
                's': {
                    'author': None,
                    'yearstring': 'year',
                    'year': 'year_int',
                    'startpage': 'startpage_int',
                    'numberofpages': 'pages_int',
                    'pages': None,
                    'edition': None,
                    'school': None,
                    'address': None,
                    'url': None,
                    'note': None,
                    'number': None,
                    'series': None,
                    'editor': None,
                    'booktitle': None,
                    'journal': None,
                    'volume': None,
                    'publisher': None,
                },
                'r': {
                    'endpage': 'endpage_int',
                    'inlg': None,
                    'inlg_code': None,
                    'subject': None,
                    'subject_headings': None,
                    'keywords': None,
                    'normalizedauthorstring': None,
                    'normalizededitorstring': None,
                    'ozbib_id': None,
                }
            }.items():
                for okey, nkey in map_.items():
                    dicts[model][nkey or okey] = row[okey]
            svalues.append(dicts['s'])
            rvalues.append(dicts['r'])
        DBSession.execute(common.Source.__table__.insert(), svalues)
        DBSession.execute(models2.Ref.__table__.insert(), rvalues)

    select(db, 'select * from refbase order by id', handler)
    DBSession.execute('COMMIT')

    for table, model, value, order in [
        ('macroarea', models2.Macroarea, lambda i, row: dict(
            pk=row['id'],
            id=slug(row['name']),
            name=row['name'],
            description=row['description']),
         None),
        ('country', models2.Country, lambda i, row: dict(
            pk=row['id'], id=row['alpha2'], name=row['name']),
         None),
        ('provider', models2.Provider, lambda i, row: dict(
            pk=row['id'],
            id=slug(row['name']),
            name=row['description'],
            description=row['comment'],
            abbr=row['abbr'],
            url=row['url'],
            refurl=row['refurl'],
            bibfield=row['bibfield']),
         None),
        ('doctype', models2.Doctype, lambda i, row: dict(
            pk=row['id'],
            id=slug(row['name']),
            abbr=row['abbr'],
            name=row['name'],
            description=row['description']),
         None),
        ('refprovider', models2.Refprovider, lambda i, row: dict(
            pk=i, provider_pk=row['provider_id'], ref_pk=row['refbase_id']),
         ('provider_id', 'refbase_id')),
        ('refdoctype', models2.Refdoctype, lambda i, row: dict(
            pk=i, doctype_pk=row['doctype_id'], ref_pk=row['refbase_id']),
         ('doctype_id', 'refbase_id')),
    ]:
        insert(db, table, model, value, order=order)

    names = dict(
        (int(d['id']), d['pk']) for d in
        insert(
            db,
            'namebase',
            common.Identifier,
            lambda i, row: dict(
                pk=i,
                id=str(row['id']),
                name=row['namestring'],
                type='name',
                description=row['nameprovider'],
                lang=row['inlg'] if row['inlg'] and len(row['inlg']) <= 3 else 'en'),
            order='id'))

    codes = dict(
        (int(d['id']), d['pk']) for d in
        insert(
            db,
            'codebase',
            common.Identifier, lambda i, row: dict(
                pk=i,
                id=str(row['id']),
                name=row['codestring'],
                type=common.IdentifierType.iso.value if row['codeprovider'] == 'ISO' else row['codeprovider']),
            start=len(names),
            order='id'))

    res = insert(
        db,
        'nodecodes',
        common.LanguageIdentifier,
        lambda i, row: dict(
            pk=i, language_pk=row['languoidbase_id'], identifier_pk=codes[row['codebase_id']]))

    insert(
        db,
        'nodenames',
        common.LanguageIdentifier,
        lambda i, row: dict(
            pk=i, language_pk=row['languoidbase_id'], identifier_pk=names[row['namebase_id']]),
        start=len(res))

    for table, model, value in [
        (
            'languoidmacroarea',
            models2.Languoidmacroarea,
            lambda i, row: dict(
                pk=i, languoid_pk=row['languoidbase_id'], macroarea_pk=row['macroarea_id'])),
        (
            'languoidcountry',
            models2.Languoidcountry,
            lambda i, row: dict(
                pk=i, languoid_pk=row['languoidbase_id'], country_pk=row['country_id'])),
        (
            'noderefs',
            common.LanguageSource,
            lambda i, row: dict(
                pk=i, language_pk=row['languoidbase_id'], source_pk=row['refbase_id'])),
        (
            'refmacroarea',
            models2.Refmacroarea,
            lambda i, row: dict(
                pk=i, macroarea_pk=row['macroarea_id'], ref_pk=row['refbase_id'])),
        (
            'refcountry',
            models2.Refcountry,
            lambda i, row: dict(
                pk=i, country_pk=row['country_id'], ref_pk=row['refbase_id'])),
        (
            'spuriousreplacements',
            models2.Superseded,
            lambda i, row: dict(
                pk=i,
                languoid_pk=row['languoidbase_id'],
                replacement_pk=row['replacement_id'],
                description=row['relation'])),

        (
            'justification',
            common.ValueSetReference,
            lambda i, row: dict(
                pk=i,
                valueset_pk=valuesets['%s%s' % (
                    'fc' if row['type'] == 'family' else 'sc', row['languoidbase_id'])],
                source_pk=row['refbase_id'],
                description=row['pages'])),
    ]:
        insert(db, table, model, value)


def prime_cache(args):
    DBSession.execute('delete from treeclosuretable')
    SQL = models2.TreeClosureTable.__table__.insert()
    ltable = models2.Languoid.__table__

    # we compute the ancestry for each single languoid
    for lid, fid in DBSession.execute('select pk, father_pk from languoid').fetchall():
        depth = 0
        DBSession.execute(SQL, dict(child_pk=lid, parent_pk=lid, depth=depth))

        # now follow up the line of ancestors
        while fid:
            depth += 1
            DBSession.execute(SQL, dict(child_pk=lid, parent_pk=fid, depth=depth))
            fid = DBSession.execute(
                sql.select([ltable.c.father_pk]).where(ltable.c.pk == fid)
            ).fetchone()[0]

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


if __name__ == '__main__':
    initializedb(create=create, prime_cache=prime_cache)
