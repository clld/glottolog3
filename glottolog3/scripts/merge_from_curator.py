# -*- coding: utf-8 -*-
import sys

import requests
from alembic.script import ScriptDirectory
from alembic.config import Config
from alembic.util import rev_id

from clld.util import parse_json_with_datetime
from clld.scripts.util import parsed_args


def main(args):  # pragma: no cover
    """local task to make changes from glottologcurator available to the production
    site via an alembic migration script.

    pulls the changelog from glottologcurator and creates a new alembic revision with it.
    """
    kw = {}
    if args.http_user and args.http_password:
        kw['auth'] = (args.http_user, args.http_password)
    changes = requests.get(args.log_url, **kw).json()

    config = Config()
    config.set_main_option("script_location", args.migrations_dir)
    scriptdir = ScriptDirectory.from_config(config)
    script = scriptdir.generate_revision(
        rev_id(), "Glottolog Curator", refresh=True,
        upgrades="""\
# from glottologcurator
    conn = op.get_bind()
    for sql, params in [
%s
    ]:
        conn.execute(sql, params)
""" % '\n'.join(u'    ("""{0}""", {1}),'.format(
        event[0], parse_json_with_datetime(event[1])) for event in changes['events']))

    args.log.info('new alembic migration script created:')
    args.log.info(script.path)
    args.log.info('run "alembic upgrade head" to merge changes')


if __name__ == '__main__':
    main(parsed_args(
        (("log_url",), {}),
        (("--http-user",), dict(default=None)),
        (("--http-password",), dict(default=None)),
    ))
    sys.exit(0)
