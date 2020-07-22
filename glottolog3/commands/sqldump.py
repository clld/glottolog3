"""
Dump the db specified in development.ini
"""
import subprocess

from clldutils.db import DB
from clld.cliutil import AppConfig


def register(parser):
    parser.add_argument('config', action=AppConfig)


def run(args):  # pragma: no cover
    fname = args.pkg_dir / 'static' / 'download' / 'glottolog.sql.gz'

    subprocess.check_call([
        'pg_dump',
        '--no-owner', '--no-privileges',
        '-Z', '9', '-f', str(fname), DB.from_settings(args.settings).name])
    assert fname.exists()
    args.log.info('{0} written'.format(fname))
