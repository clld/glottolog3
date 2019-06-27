import os
import re
import sys
import gzip
import shutil
import argparse
import subprocess
import collections
from datetime import datetime
from urllib.request import urlretrieve

import configparser

from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config, create_engine

import transaction
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from clldutils.clilib import ArgumentParserWithLogging, command, ParserError
from clldutils.path import Path, write_text, md5, as_unicode
from clldutils.jsonlib import load, update
from clldutils.apilib import assert_release
from csvw.dsv import UnicodeWriter
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
    version = assert_release(args.repos.repos)
    cfg = get_release_config()
    last = sorted(set(cfg.sections()) - {version}, key=lambda s: float(s[1:]))[-1][1:]
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
        l.split(b'|')[0].decode('utf8') for l in
        subprocess.check_output(['psql', '-l', '-t', '-A']).splitlines()]
    if dbname in dbs:
        log.warn('db {0} exists! Drop first to recreate.'.format(dump.name))
    else:
        if not dump.exists():
            _download_sql_dump(rel, log)
        subprocess.check_call(['createdb', dbname])
        subprocess.check_call(['psql', '-d', dbname, '-f', str(dump)])
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
def x(args):
    try:
        from cdstarcat.catalog import Catalog
    except ImportError:
        args.log.error('pip install cdstarcat')
        return
    fname = args.pkg_dir.joinpath('static', 'downloads.json')
    downloads = load(fname)
    release = args.args[0]
    with Catalog(
            Path(os.environ['CDSTAR_CATALOG']),
            cdstar_url=os.environ['CDSTAR_URL'],
            cdstar_user=os.environ['CDSTAR_USER'],
            cdstar_pwd=os.environ['CDSTAR_PWD']) as cat:
        obj = cat.api.get_object(uid=downloads[release]['oid'])
        bitstreams = obj.bitstreams[:]
        for bs in bitstreams:
            print(bs.id, bs._properties)


@command()
def cdstar(args):
    try:
        from cdstarcat.catalog import Catalog
    except ImportError:
        args.log.error('pip install cdstarcat')
        return

    #
    # FIXME: look up oid for release in downloads.json! if it exists, replace the bitstreams
    # rather than creating a new object!
    #
    dlfname = args.pkg_dir.joinpath('static', 'downloads.json')
    downloads = load(dlfname)
    release = args.args[0]
    title_pattern = re.compile('glottolog (?P<version>[0-9.]+) - downloads')
    with Catalog(
            Path(os.environ['CDSTAR_CATALOG']),
            cdstar_url=os.environ['CDSTAR_URL'],
            cdstar_user=os.environ['CDSTAR_USER'],
            cdstar_pwd=os.environ['CDSTAR_PWD']) as cat:
        #
        # FIXME: there must be a way to overwrite old releases in case of bugfixes!
        #
        if release in downloads:
            # This is a bugfix release, we don't have to create a new object on CDSTAR!
            obj = cat.api.get_object(uid=downloads[release]['oid'])
        else:
            obj = cat.api.get_object()
            obj.metadata = {
                "creator": "pycdstar",
                "title": "glottolog %s - downloads" % release,
                "description": "Custom downloads for release %s of "
                               "[Glottolog](http://glottolog.org)" % release,
            }
        bitstreams = obj.bitstreams[:]
        for fname in args.pkg_dir.joinpath('static', 'download').iterdir():
            if fname.is_file() and not fname.name.startswith('.'):
                bsname = fname.name.replace('-', '_')
                bitstream, skip = None, False
                for bitstream in bitstreams:
                    if bitstream.id == bsname:
                        break
                else:
                    bitstream = None
                if bitstream:
                    if bitstream._properties['checksum'] != md5(fname):
                        bitstream.delete()
                    else:
                        skip = True
                        print('skipping {0}'.format(fname.name))
                if not skip:
                    print(fname.name)
                    obj.add_bitstream(fname=fname.as_posix(), name=bsname)
        cat.add(obj, update=True)

    with update(dlfname, default=collections.OrderedDict(), indent=4, sort_keys=True) as downloads:
        for oid, spec in load(Path(os.environ['CDSTAR_CATALOG'])).items():
            if 'metadata' in spec and 'title' in spec['metadata']:
                match = title_pattern.match(spec['metadata']['title'])
                if match:
                    if (match.group('version') not in downloads) or match.group('version') == release:
                        args.log.info('update info for release {0}'.format(match.group('version')))
                        spec['oid'] = oid
                        downloads[match.group('version')] = spec
    args.log.info('{0} written'.format(dlfname))
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
    nodes = collections.OrderedDict((l.id, l) for l in args.repos.languoids())
    trees = []
    for lang in nodes.values():
        if not lang.lineage and not lang.category.startswith('Pseudo '):
            ns = lang.newick_node(nodes=nodes).newick
            if lang.level == args.repos.languoid_levels.language and not ns.startswith('('):
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
        ma_param = common.Parameter.get('macroarea')
        for l in DBSession.query(models.Languoid)\
                .filter(or_(
                    models.Languoid.level == models.LanguoidLevel.dialect,
                    models.Languoid.level == models.LanguoidLevel.language))\
                .options(
                    joinedload(common.Language.valuesets)
                        .joinedload(common.ValueSet.values)
                        .joinedload(common.Value.domainelement),
                    joinedload(common.Language.languageidentifier)
                        .joinedload(common.LanguageIdentifier.identifier))\
                .order_by(common.Language.name):
            macroareas = []
            for vs in l.valuesets:
                if vs.parameter_pk == ma_param.pk:
                    macroareas = [v.domainelement.name for v in vs.values]
                    break
            writer.writerow([
                l.id,
                l.name,
                ' '.join(
                    i.name for i in l.get_identifier_objs(common.IdentifierType.iso)),
                l.level,
                macroareas[0] if macroareas else '',
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
def dbinit(args):  # pragma: no cover
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


def db_url(args):
    config = args.pkg_dir.parent / 'development.ini'
    settings = get_appsettings(str(config))
    engine = engine_from_config(settings, 'sqlalchemy.')
    return engine.url


def with_session(args):
    setup_session(args.pkg_dir.parent.joinpath('development.ini').as_posix())


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
