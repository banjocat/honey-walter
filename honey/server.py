import sys

import yaml
from twisted.conch import recvline, avatar
from twisted.conch.interfaces import IConchUser, ISession
from twisted.conch.ssh import keys, session
from twisted.cred import checkers
from twisted.cred.portal import Portal, IRealm
from twisted.internet import reactor
from twisted.conch.ssh.factory import SSHFactory
from zope.interface import implementer
from twisted.python import log


log.startLogging(sys.stdout)


class HoneyProtocol(recvline.HistoricRecvLine):
    '''
    This is the bulk of the logic that handles all connections
    '''
    def __init__(self):
        log.msg('Protocol created')

    def newLine(self):
        self.terminal.write('\n\r$ ')

    def showPrompt(self):
        self.terminal.write('\n\r')
        self.terminal.write('$ ')

    def connectionMade(self):
        log.msg('Connection made')
        self.terminal.write(CONFIG['motd'])
        # self.terminal.nextLine()
        self.showPrompt()

    def lineRecevied(self, line):
        line = line.strip()
        if line:
            self.terminal.write(line)
            # self.terminal.nextLine()

    def dataReceived(self, data):
        if data == '\r':
            self.newLine()
        self.terminal.write(data)


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
        protocol = HoneyProtocol()
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


def _get_config():
    '''
    setups the config from config.yml

    TODO: This should really validate it as well for required parts
    '''
    with open('./config.yml') as config_file:
        text = config_file.read()

    config = yaml.load(text)
    return config


def _create_private_and_public_keys():
    with open('./demo.pem') as pipe:
        private_blob = pipe.read()
        private_key = keys.Key.fromString(data=private_blob)

    with open('./demo.pub') as pipe:
        public_blob = pipe.read()
        public_key = keys.Key.fromString(data=public_blob)

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
    log.msg('Reading config')
    global CONFIG
    CONFIG = _get_config()
    log.msg('Config:')
    log.msg('Creating checker')
    checker = _get_checker()
    log.msg('Creating portal')
    portal = _get_portal(checker)
    log.msg('Setting up factory')
    factory = _get_and_setup_factory(checker, portal)
    reactor.listenTCP(CONFIG['port'], factory)
    log.msg('Starting up')
    reactor.run()
