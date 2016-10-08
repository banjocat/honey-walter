import logging

from twisted.conch import manhole, avatar
from twisted.conch.interfaces import IConchUser, ISession
from twisted.conch.ssh import keys, session
from twisted.cred import checkers
from twisted.cred.portal import Portal, IRealm
from twisted.internet import reactor
from twisted.conch.insults import insults
from twisted.conch.ssh.factory import SSHFactory
from zope.interface import implementer

import honey_logging
from config import CONFIG
from parser import parse_input


class HoneyProtocol(manhole.Manhole):
    '''
    This is the bulk of the logic that handles all connections
    '''

    def __init__(self, user):
        self.user = user
        address = self.user.transport.getPeer().address
        self.log_data = self.get_avatar_identifier_dict(address)

    def showPrompt(self):
        self.terminal.nextLine()
        self.terminal.write('$ ')

    def connectionMade(self):
        '''
        Called once on initial connection of an Avatar
        '''
        logging.info('Connection made')
        super(HoneyProtocol, self).connectionMade()
        self.log_stash('login')
        self.terminal.write(CONFIG['motd'])
        self.showPrompt()

    def log_stash(self, msg):
        honey_logging.stash.info(msg, extra=self.log_data)

    def get_avatar_identifier_dict(self, address):
        '''
        Every logstash message has this data
        '''
        data = {
                'protocol': address.type,
                'ip': address.host,
                'port': address.port
                }
        return data

    def lineReceived(self, line):
        '''
        Called everytime an avatar sends a line
        This is where logging and output is done
        '''
        command = line.strip()
        output = parse_input(command)
        self.log_data['command'] = command
        self.log_stash('command')
        self.terminal.write(output)
        self.showPrompt()

    def handle_INT(self):
        '''
        The default INT handler is sloppy
        Replaced it with something that is more expected
        '''
        self.terminal.write('^C')
        self.showPrompt()


@implementer(ISession)
class HoneyAvatar(avatar.ConchUser):
    '''
    An avatar represents one user logged in
    '''

    def __init__(self, username):
        logging.info('Avatar being created')
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session': session.SSHSession})

    def openShell(self, transport):
        logging.info('Protocol being setup')
        self.transport = transport
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
            logging.info('Interface IConchUser found')
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
    logging.info('Creating checker')
    checker = _get_checker()
    logging.info('Creating portal')
    portal = _get_portal(checker)
    logging.info('Setting up factory')
    factory = _get_and_setup_factory(checker, portal)
    reactor.listenTCP(CONFIG['port'], factory)
    logging.info('Starting up')
    reactor.run()
