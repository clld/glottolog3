from __future__ import unicode_literals, print_function, division

import os
import re
import sys
import gzip
import shutil
import argparse
import subprocess
import collections
from datetime import datetime

import configparser
from six.moves.urllib.request import urlretrieve

from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config, create_engine

import transaction
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, joinedload_all

from clldutils.clilib import ArgumentParserWithLogging, command, ParserError
from clldutils.path import Path, write_text, md5, as_unicode
from clldutils.jsonlib import load, update, dump
from clldutils.dsv import UnicodeWriter
from clld.scripts.util import setup_session
from clld.db.meta import DBSession
from clld.db.models import common
from pyglottolog import Glottolog

import glottolog3
from glottolog3 import models
from glottolog3 import initdb
from glottolog3 import static_archive

RELEASES = Path(__file__).parent / 'releases.ini'


def get_release_config(filepath=RELEASES, encoding='utf-8'):
    cfg = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with filepath.open(encoding=encoding) as f:
        cfg.read_file(f)
    return cfg


def get_release(version):
    cfg = get_release_config()
    return next(cfg[section] for section in cfg.sections()
                if cfg.get(section, 'version') == version)


def _download_sql_dump(rel, log):
    target = Path('glottolog-{0}.sql.gz'.format(rel['version']))
    log.info('retrieving {0}'.format(rel['sql_dump_url']))
    urlretrieve(rel['sql_dump_url'], target.as_posix())
    assert md5(target) == rel['sql_dump_md5']
    unpacked = target.with_suffix('')
    with gzip.open(target.as_posix()) as f, unpacked.open('wb') as u:
        shutil.copyfileobj(f, u)
    target.unlink()
    log.info('SQL dump for Glottolog release {0} written to {1}'.format(
        rel['version'], unpacked))


@command()
def mark_new_languages(args):
    cfg = get_release_config()
    last = sorted(cfg.sections(), key=lambda s: float(s[1:]))[-1][1:]
    cdb = create_engine('postgresql://postgres@/glottolog3')
    ldb = create_engine('postgresql://postgres@/glottolog-{0}'.format(last))
    sql = "select id from language as l, languoid as ll where l.pk = ll.pk and ll.level = 'language'"
    current = set(r[0] for r in cdb.execute(sql))
    last = set(r[0] for r in ldb.execute(sql))
    for gc in sorted(current - last):
        cdb.execute(
            "update language set updated = %s where id = %s", (datetime.utcnow(), gc))


@command()
def download_sql_dump(args):
    rel = get_release(args.args[0])
    _download_sql_dump(rel, args.log)


def _load_sql_dump(rel, log):
    dump = Path('glottolog-{0}.sql'.format(rel['version']))
    dbname = as_unicode(dump.stem)
    dbs = [
        l.split('|')[0] for l in
        subprocess.check_output(['psql', '-l', '-t', '-A']).splitlines()]
    if dbname in dbs:
        log.warn('db {0} exists! Drop first to recreate.'.format(dump.name))
    else:
        if not dump.exists():
            _download_sql_dump(rel, log)
        subprocess.check_call(['createdb', dbname])
        subprocess.check_call(['psql', '-d', dbname, '-f', dump.name])
        log.info('db {0} created'.format(dbname))


@command()
def load_sql_dump(args):
    rel = get_release(args.args[0])
    _load_sql_dump(rel, args.log)


@command()
def create_archive(args):
    rels = get_release_config()
    for section in rels.sections():
        _load_sql_dump(rels[section], args.log)
    out = Path('archive')
    if args.args:
        out = Path(args.args[0])
    static_archive.create([rels.get(sec, 'version') for sec in rels.sections()], out)
    args.log.info('static archive created in {0}'.format(out))


@command()
def cdstar(args):
    try:
        from cdstarcat.catalog import Catalog
    except ImportError:
        args.log.error('pip install cdstarcat')
        return

    title_pattern = re.compile('glottolog (?P<version>[0-9.]+) - downloads')
    with Catalog(
            Path(os.environ['CDSTAR_CATALOG']),
            cdstar_url=os.environ['CDSTAR_URL'],
            cdstar_user=os.environ['CDSTAR_USER'],
            cdstar_pwd=os.environ['CDSTAR_PWD']) as cat:
        obj = cat.api.get_object()
        obj.metadata = {
            "creator": "pycdstar",
            "title": "glottolog %s - downloads" % args.args[0],
            "description": "Custom downloads for release %s of "
                           "[Glottolog](http://glottolog.org)" % args.args[0],
        }
        for fname in args.pkg_dir.joinpath('static', 'download').iterdir():
            if fname.is_file() and not fname.name.startswith('.'):
                print(fname.name)
                obj.add_bitstream(
                    fname=fname.as_posix(), name=fname.name.replace('-', '_'))
        cat.add(obj)

    fname = args.pkg_dir.joinpath('static', 'downloads.json')
    with update(fname, default={}, indent=4) as downloads:
        for oid, spec in load(Path(os.environ['CDSTAR_CATALOG'])).items():
            if 'metadata' in spec and 'title' in spec['metadata']:
                match = title_pattern.match(spec['metadata']['title'])
                if match:
                    if match.group('version') not in downloads:
                        spec['oid'] = oid
                        downloads[match.group('version')] = spec
    args.log.info('{0} written'.format(fname))
    args.log.info('{0}'.format(os.environ['CDSTAR_CATALOG']))


@command()
def sqldump(args):
    db = db_url(args)
    fname = args.pkg_dir / 'static' / 'download' / 'glottolog.sql.gz'
    subprocess.check_call([
        'pg_dump',
        '-U', db.username, '--no-owner', '--no-privileges',
        '-Z', '9', '-f', str(fname), db.database])
    assert fname.exists()
    args.log.info('{0} written'.format(fname))


@command()
def newick(args):
    from pyglottolog.languoids import Level
    nodes = collections.OrderedDict((l.id, l) for l in args.repos.languoids())
    trees = []
    for lang in nodes.values():
        if not lang.lineage and not lang.category.startswith('Pseudo '):
            ns = lang.newick_node(nodes=nodes).newick
            if lang.level == Level.language and not ns.startswith('('):
                # an isolate without dialects: we wrap it in a pseudo-family with the
                # same name and ID.
                ns = '({0}){0}'.format(ns)
            trees.append('{0};'.format(ns))
    fname = args.pkg_dir.joinpath('static', 'download', 'tree-glottolog-newick.txt')
    write_text(fname, '\n'.join(trees))
    args.log.info('{0} written'.format(fname))


@command()
def geo(args):
    with_session(args)
    fname = args.pkg_dir.joinpath('static', 'download', 'languages-and-dialects-geo.csv')
    with transaction.manager, UnicodeWriter(fname) as writer:
        writer.writerow([
            'glottocode',
            'name',
            'isocodes',
            'level',
            'macroarea',
            'latitude',
            'longitude'])
        for l in DBSession.query(models.Languoid)\
                .filter(or_(
                    models.Languoid.level == models.LanguoidLevel.dialect,
                    models.Languoid.level == models.LanguoidLevel.language))\
                .options(
                    joinedload(models.Languoid.macroareas),
                    joinedload_all(
                        common.Language.languageidentifier,
                        common.LanguageIdentifier.identifier))\
                .order_by(common.Language.name):
            writer.writerow([
                l.id,
                l.name,
                ' '.join(
                    i.name for i in l.get_identifier_objs(common.IdentifierType.iso)),
                l.level,
                l.macroareas[0].name if l.macroareas else '',
                l.latitude if l.latitude is not None else '',
                l.longitude if l.longitude is not None else ''])

    args.log.info('{0} written'.format(fname))


@command(name='downloads')
def downloads(args):
    newick(args)
    geo(args)
    sqldump(args)


@command()
def dbload(args):
    with_session(args)
    with transaction.manager:
        initdb.load(args)


@command()
def dbprime(args):
    with_session(args)
    with transaction.manager:
        initdb.prime(args)


@command()
def dbinit(args):
    """
    glottolog-app dbinit VERSION
    """
    if not args.args:
        raise ParserError('not enough arguments')
    db = db_url(args)
    args.log.info('dropping DB {0}'.format(db.database))
    try:
        subprocess.check_call([
            'dropdb', '-U', db.username, '--if-exists', db.database])
    except subprocess.CalledProcessError:
        args.log.error('could not drop DB, maybe other processes are still accessing it.')
        return
    args.log.info('creating DB {0}'.format(db.database))
    subprocess.check_call(['createdb', '-U', db.username, db.database])
    dbload(args)
    dbprime(args)


@command()
def ldstatus(args):
    from glottolog3.langdocstatus import extract_data

    endangerment = {
        l.id: l.cfg['endangerment']
        for l in args.repos.languoids() if 'endangerment' in l.cfg}
    with_session(args)
    dump(extract_data(endangerment), 'glottolog3/static/ldstatus.json', indent=4)


def db_url(args):
    config = args.pkg_dir.parent / 'development.ini'
    settings = get_appsettings(str(config))
    engine = engine_from_config(settings, 'sqlalchemy.')
    return engine.url


def with_session(args):
    setup_session(args.pkg_dir.parent.joinpath('development.ini').as_posix())

@command()
def add_languoid(args):
    with_session(args)
    with transaction.manager:
        DBSession.add(models.Languoid(id="test0000",
                                      name="test1",
                                      level=models.LanguoidLevel.from_string('dialect')))

def main():  # pragma: no cover
    pkg_dir = Path(glottolog3.__file__).parent
    parser = ArgumentParserWithLogging('glottolog3')
    parser.add_argument(
        '--repos',
        help="path to glottolog data repository",
        type=Glottolog,
        default=Glottolog(
            Path(glottolog3.__file__).parent.parent.parent.joinpath('glottolog')))
    parser.add_argument('--pkg-dir', help=argparse.SUPPRESS, default=pkg_dir)
    sys.exit(parser.main())


if __name__ == '__main__':
    main()
