from fabric.api import task, run, env, cd, settings
from fabtools import require

env.hosts = ["op@devel.quintagroup.com"]
env.forward_agent = True


@task
def init_slave():
    init("slave")


def init(branch="master"):
    require.git.working_copy("ssh://op@projects.qg/load_testing.git",
                             branch=branch, update=True)
    with cd('load_testing'):
        run('python bootstrap.py')
        run('bin/buildout')

        run('cat etc/circus.ini')
        with settings(warn_only=True):
            result = run('bin/circusctl status')

        if result.failed:
            run('bin/circusd --daemon --pidfile circusd.pid')

        run('bin/circusctl restart slave')
