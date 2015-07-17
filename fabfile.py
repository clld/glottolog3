from fabric.api import task, local, cd, put, hosts, sudo, execute

from clldfabric.util import working_directory
from clldfabric import tasks
tasks.init('glottolog3')


def bin(name):
    return '/home/robert/venvs/clld/bin/' + name


def run_script(name):
    local('%s glottolog3/scripts/%s.py development.ini' % (bin('python'), name))


@hosts(tasks.APP.production)
@task
def copy_treefiles():
    with working_directory('glottolog3/static/'):
        local('tar -czvf trees.tgz trees')
        put('trees.tgz', '/tmp')

    with cd('/usr/venvs/glottolog3/src/glottolog3/glottolog3/static'):
        sudo('mv /tmp/trees.tgz .')
        sudo('tar -xzvf trees.tgz')
        sudo('chown -R root:root trees')


@hosts(tasks.APP.production)
@task
def recreate_treefiles():
    run_script('compute_treefiles')
    execute(copy_treefiles)
