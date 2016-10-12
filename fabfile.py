from fabric.api import settings, hosts, run, put


@hosts('jackmuratore.com')
def deploy():
    with settings(user='root'):
        put('./puppet', '/tmp')
        run('puppet apply --modulepath /tmp/puppet/modules:/etc/puppet/modules /tmp/puppet/init.pp')


@hosts('jackmuratore.com')
def install_puppet():
    with settings(user='root'):
        run('apt-get install -y puppet')
        run('/etc/init.d/puppet stop')
        run('puppet module install garethr-docker')
