"""
Dump the db specified in development.ini
"""
import subprocess

from clldutils.db import DB
from clld.scripts.util import get_env_and_settings


def run(args):
    _, settings = get_env_and_settings(args.pkg_dir.parent / 'development.ini')
    fname = args.pkg_dir / 'static' / 'download' / 'glottolog.sql.gz'

    subprocess.check_call([
        'pg_dump',
        '--no-owner', '--no-privileges',
        '-Z', '9', '-f', str(fname), DB.from_settings(settings).name])
    assert fname.exists()
    args.log.info('{0} written'.format(fname))
