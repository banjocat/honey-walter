from twisted.conch.ssh.factory import SSHFactory
from twisted.conch.ssh.keys import Key
from twisted.cred.portal import Portal
from twisted.internet import reactor


with open('./demo.pem') as pipe:
    private_blob = pipe.read()
    private_key = Key.fromString(data=private_blob)

with open('./demo.pub') as pipe:
    public_blob = pipe.read()
    public_key = Key.fromString(data=public_blob)

factory = SSHFactory()
factory.privateKeys = {'ssh-rsa': private_key}
factory.publicKeys = {'ssh-rsa': public_key}
factory.portal = Portal(None)


reactor.listenTCP(2000, factory)

reactor.run()
