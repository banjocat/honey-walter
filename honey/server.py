import sys

from twisted.conch import manhole, avatar
from twisted.conch.interfaces import IConchUser, ISession
from twisted.conch.ssh import keys, session
from twisted.cred import checkers
from twisted.cred.portal import Portal, IRealm
from twisted.internet import reactor
from twisted.conch.insults import insults
from twisted.conch.ssh.factory import SSHFactory
from zope.interface import implementer
from twisted.python import log

from config import CONFIG
from parser import parse_input


log.startLogging(sys.stdout)


class HoneyProtocol(manhole.Manhole):
    '''
    This is the bulk of the logic that handles all connections
    '''
    def __init__(self, user):
        self.user = user

    def showPrompt(self):
        self.terminal.write('$ ')

    def connectionMade(self):
        log.msg('Connection made')
        super(HoneyProtocol, self).connectionMade()
        self.terminal.write(CONFIG['motd'])
        self.terminal.nextLine()
        self.showPrompt()

    def lineReceived(self, line):
        log.msg('line received')
        command = line.strip()
        output = parse_input(command)
        log.msg('output:', output)
        self.terminal.write(output)
        self.terminal.nextLine()
        self.showPrompt()

    def handle_INT(self):
        self.terminal.write('^C')
        self.terminal.nextLine()
        self.showPrompt()


@implementer(ISession)
class HoneyAvatar(avatar.ConchUser):
    '''
    An avatar represents one user logged in
    '''

    def __init__(self, username):
        log.msg('Avatar being created')
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session': session.SSHSession})

    def openShell(self, transport):
        log.msg('Protocol being setup')
        protocol = insults.ServerProtocol(HoneyProtocol, self)
        protocol.makeConnection(transport)
        transport.makeConnection(session.wrapProtocol(protocol))

    def getPty(self, terminal, windowSize, attrs):
        return None

    def eofReceived(self):
        pass

    def closed(self):
        pass


@implementer(IRealm)
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


def _create_private_and_public_keys():
    private_key = keys.Key.fromString(data=CONFIG['pem_key'])
    public_key = keys.Key.fromString(data=CONFIG['pub_key'])

    return (private_key, public_key)


def _get_and_setup_factory(checker, portal):
    '''
    creates and adds sshkeys and portal to factory
    '''
    factory = SSHFactory()
    (private_key, public_key) = _create_private_and_public_keys()
    factory.privateKeys = {'ssh-rsa': private_key}
    factory.publicKeys = {'ssh-rsa': public_key}
    factory.portal = portal
    return factory


def _get_checker():
    '''
    creates login:password based on config
    '''
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse()
    checker.addUser(CONFIG['username'], CONFIG['password'])
    return checker


def _get_portal(checker):
    '''
    creates portal and adds realm and checker
    '''
    portal = Portal(HoneyRealm())
    portal.registerChecker(checker)
    return portal


if __name__ == '__main__':
    log.msg('Creating checker')
    checker = _get_checker()
    log.msg('Creating portal')
    portal = _get_portal(checker)
    log.msg('Setting up factory')
    factory = _get_and_setup_factory(checker, portal)
    reactor.listenTCP(CONFIG['port'], factory)
    log.msg('Starting up')
    reactor.run()
