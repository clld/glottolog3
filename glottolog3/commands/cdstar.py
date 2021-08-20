"""
Sync Glottolog downloads with CDSTAR
"""
import os
import re
import pathlib
import argparse
import collections

from clldutils.jsonlib import load, update
from clldutils.path import md5
from clldutils.clilib import ParserError


def register(parser):  # pragma: no cover
    try:
        from cdstarcat.catalog import Catalog
    except ImportError:
        raise ParserError('pip install cdstarcat')
    parser.add_argument('version', help="version number without 'v' prefix")
    parser.add_argument(
        '--catalog', type=pathlib.Path, default=pathlib.Path(os.environ.get('CDSTAR_CATALOG') or 'cat.json'))
    parser.add_argument('--url', default=os.environ.get('CDSTAR_URL'))
    parser.add_argument('--user', default=os.environ.get('CDSTAR_USER'))
    parser.add_argument('--pwd', default=os.environ.get('CDSTAR_PWD'))
    parser.add_argument('--catalog_class', help=argparse.SUPPRESS, default=Catalog)


def run(args):  # pragma: no cover
    #
    # FIXME: look up oid for release in downloads.json! if it exists, replace the bitstreams
    # rather than creating a new object!
    #
    dlfname = args.pkg_dir.joinpath('static', 'downloads.json')
    downloads = load(dlfname)
    release = args.version
    title_pattern = re.compile('glottolog (?P<version>[0-9.]+) - downloads')
    with args.catalog_class(args.catalog, args.url, args.user, args.pwd) as cat:
        #
        # FIXME: there must be a way to overwrite old releases in case of bugfixes!
        #
        if release in downloads:
            print('adding bitstreams to {0}'.format(downloads[release]['oid']))
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
        obj.read()
        cat.add(obj, update=True)

    with update(dlfname, default=collections.OrderedDict(), indent=4, sort_keys=True) as downloads:
        for oid, spec in load(args.catalog).items():
            if 'metadata' in spec and 'title' in spec['metadata']:
                match = title_pattern.match(spec['metadata']['title'])
                if match:
                    if (match.group('version') not in downloads) or match.group('version') == release:
                        args.log.info('update info for release {0}'.format(match.group('version')))
                        spec['oid'] = oid
                        downloads[match.group('version')] = spec
    args.log.info('{0} written'.format(dlfname))
    args.log.info('{0}'.format(args.catalog))
