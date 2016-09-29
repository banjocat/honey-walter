import sys

from twisted.conch import recvline, avatar
from twisted.conch.interfaces import IConchUser
from twisted.conch.ssh import keys, session
from twisted.cred import portal, checkers
from twisted.internet import reactor
from twisted.conch.ssh.factory import SSHFactory
from zope.interface import implements
from twisted.python import log


log.startLogging(sys.stdout)

with open('./demo.pem') as pipe:
    private_blob = pipe.read()
    private_key = keys.Key.fromString(data=private_blob)

with open('./demo.pub') as pipe:
    public_blob = pipe.read()
    public_key = keys.Key.fromString(data=public_blob)

class HoneyRealm(object):
    implements(portal.IRealm)
    def requestAvatar(self, avatarId, mind, *interfaces):
        print avatarId, mind
        pass

class HoneyProtocol(recvline.HistoricRecvLine):
    def __init__(self, user):
        self.user = user

    def connectionMade(self):
        self.showPrompt()

    def showPrompt(self):
        self.terminal.write("$ ")


class HoneyAvatar(avatar.ConchUser):
    implements(IConchUser)

    def __init__(self, username):
        log.msg(username)
        avatar.ConchUser.__init__(self)
        self.username = username

class HoneyRealm(object):
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IConchUser in interfaces:
            return interfaces[0], HoneyAvatar(avatarId), lambda: None
        else:
            raise NotImplementedError("No supported interfaces found")


factory = SSHFactory()
factory.privateKeys = {'ssh-rsa': private_key}
factory.publicKeys = {'ssh-rsa': public_key}
checker = checkers.InMemoryUsernamePasswordDatabaseDontUse()
checker.addUser('root', 'password')
portal = portal.Portal(HoneyRealm())
portal.registerChecker(checker)

factory.portal = portal



reactor.listenTCP(2000, factory)

log.msg('Starting up')
reactor.run()
