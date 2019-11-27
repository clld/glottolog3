"""
Recreate the glottolog3 database
"""
from clld.scripts.util import get_env_and_settings
from clldutils.db import FreshDB
from clldutils.apilib import assert_release
from clldutils.clilib import ParserError
import transaction

from glottolog3 import initdb
from glottolog3.cli_util import with_session


def dbload(args):
    with_session(args)
    with transaction.manager:
        initdb.load(args)


def dbprime(args):
    with_session(args)
    with transaction.manager:
        initdb.prime(args)


def run(args):  # pragma: no cover
    try:
        args.version = assert_release(args.repos.repos)
    except AssertionError:
        raise ParserError('glottolog-data must be checked out at release tag!')

    _, settings = get_env_and_settings(str(args.pkg_dir.parent / 'development.ini'))
    with FreshDB.from_settings(settings, log=args.log):
        dbload(args)
        dbprime(args)
