from getpass import getpass

import requests
from path import path
from fabric.api import task
from alembic.script import ScriptDirectory
from alembic.config import Config
from alembic.util import rev_id

from clld.deploy import tasks
tasks.init('glottolog3')


@task
def alembic_revision(log_url):
    """local task to merge changes from glottologcurator available to the production
    site via an alembic migration script.

    pulls the changelog from glottologcurator and create a new alembic revision with it.
    """
    user = raw_input('HTTP Basic auth user for glottologcurator: ')
    password = getpass('HTTP Basic auth password for glottologcurator: ')
    kw = {}
    if user and password:
        kw['auth'] = (user, password)
    changes = requests.get(log_url, **kw).json()

    config = Config()
    config.set_main_option("script_location", path('.').joinpath('migrations'))
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
""" % '\n'.join(u'    ("""{0}""", {1}),'.format(*event) for event in changes['events']))

    print('new alembic migration script created:')
    print(script.path)
