import sys

from twisted.conch import recvline, avatar
from twisted.conch.interfaces import IConchUser
from twisted.conch.ssh import keys, session
from twisted.cred import portal, checkers
from twisted.internet import reactor
from twisted.conch.ssh.factory import SSHFactory
from zope.interface import implementer
from twisted.python import log


log.startLogging(sys.stdout)

with open('./demo.pem') as pipe:
    private_blob = pipe.read()
    private_key = keys.Key.fromString(data=private_blob)

with open('./demo.pub') as pipe:
    public_blob = pipe.read()
    public_key = keys.Key.fromString(data=public_blob)



class HoneyProtocol(recvline.HistoricRecvLine):
    def __init__(self, user):
        self.user = user

    def connectionMade(self):
        log.msg('connection made')
        self.showPrompt()

    def showPrompt(self):
        self.terminal.write('$ ')



@implementer(IConchUser)
class HoneyAvatar(avatar.ConchUser):
    '''
    An avatar represents one user logged in
    '''

    def __init__(self, username):
        log.msg('username:', username)
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session': session.SSHSession})

    def openShell(transport):
        log.msg('Opening shell')
        protocol = HoneyProtocol()
        protocol.makeConnection(transport)
        transport.makeConnection(session.wrapProtocol(protocol))
        log.msg('Shell created')

    def getPty(self, **args):
        return None

    def eofReceived(self):
        pass

    def closed(self):
        pass


@implementer(portal.IRealm)
class HoneyRealm(object):
    '''
    A realm is a factory that returns avatars after authentication is made
    '''

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IConchUser in interfaces:
            log.msg('Interface IConchUser found')
            return interfaces[0], HoneyAvatar(avatarId), lambda: None
        else:
            raise NotImplementedError('No supported interfaces found')


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
