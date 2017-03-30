# coding: utf8
from __future__ import unicode_literals, print_function, division
import os
import sys
import argparse
import re
from collections import OrderedDict
import subprocess

import transaction
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, joinedload_all
from clldutils.clilib import ArgumentParserWithLogging, command, ParserError
from clldutils.path import Path, write_text
from clldutils.jsonlib import load, update
from clldutils.dsv import UnicodeWriter
from clld.scripts.util import setup_session
from clld.db.meta import DBSession
from clld.db.models import common
from pyglottolog.api import Glottolog

import glottolog3
from glottolog3 import models
from glottolog3 import initdb

DB = glottolog3.__name__


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
    fname = args.pkg_dir.joinpath('static', 'download', 'glottolog.sql')
    subprocess.check_call(['pg_dump', '-x', '-O', '-f', fname.as_posix(), DB])
    subprocess.check_call(['gzip', fname.as_posix()])
    fname = fname.parent.joinpath(fname.name + '.gz')
    assert fname.exists()
    args.log.info('{0} written'.format(fname))


@command()
def newick(args):
    from pyglottolog.objects import Level
    nodes = OrderedDict([(l.id, l) for l in args.repos.languoids()])
    trees = []
    for lang in nodes.values():
        if not lang.lineage and not lang.category.startswith('Pseudo '):
            ns = lang.newick_node(nodes=nodes).newick
            if lang.level == Level.language:
                # an isolate: we wrap it in a pseudo-family with the same name and ID.
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
    cdstar(args)


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
    args.log.info('dropping DB {0}'.format(DB))
    try:
        subprocess.check_call(['dropdb', DB])
    except subprocess.CalledProcessError:
        args.log.error('could not drop DB, maybe other processes are still accessing it.')
        return
    args.log.info('creating DB {0}'.format(DB))
    subprocess.check_call(['createdb', DB])
    dbload(args)
    dbprime(args)


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
