import requests
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
    After authentication and Avatar(user) creation
    This is where all connections end up.
    Async calls at lineReceived
    Manhole protocol has a lot of magic.
    It gives a line history and has a rough emulation of a terminal.
    '''

    def __init__(self, avatar):
        '''
        An avatar is a user.
        avatar.transport is attached during avatar creation.
        It has information about how the connection was made.
        IP being the most important information.
        self.log_data are the fields that will always be sent to logstash
        '''
        self.avatar = avatar
        address = self.avatar.transport.getPeer().address
        self.transport = self.avatar.transport
        ip = address.host
        self.location = ip_to_location(ip)

    def showPrompt(self):
        self.terminal.nextLine()
        self.terminal.write('$ ')

    def connectionMade(self):
        '''
        Called once after authentication and avatar creation
        '''
        honey_logging.console.info('Connection made')
        super(HoneyProtocol, self).connectionMade()
        self.log_stash('login')
        self.terminal.write(CONFIG['motd'])
        self.showPrompt()

    def connectionLost(self, reason):
        self.log_stash('logout', reason)
        super(HoneyProtocol, self).connectionLost(reason)

    def log_stash(self, action, output=None):
        '''
        Creates and sends a message to logstash
        '''
        data = {
                'ip': self.location['ip'],
                'country': self.location['country_code'],
                'region': self.location['region_code'],
                'city': self.location['city'],
                'action': action,
                'output': output
                }
        honey_logging.stash.info('logstash-honey', extra=data)

    def lineReceived(self, line):
        '''
        Called everytime an avatar sends a line
        This is where logging and output is done
        '''
        command = line.strip()
        self.log_stash('command', command)
        if command == 'exit':
            self.transport.loseConnection()
            return
        output = parse_input(command)
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
        honey_logging.console.info('Avatar being created')
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session': session.SSHSession})

    def openShell(self, transport):
        honey_logging.console.info('Protocol being setup')
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
            honey_logging.console.info('Interface IConchUser found')
            return interfaces[0], HoneyAvatar(avatarId), lambda: None
        else:
            raise NotImplementedError('No supported interfaces found')


class HoneyFactory(SSHFactory):

    def getService(self, transport, service):
        ip = transport.getPeer().address.host
        location = ip_to_location(ip)
        data = {
                'ip': location['ip'],
                'country': location['country_code'],
                'region': location['region_code'],
                'city': location['city'],
                'action': 'auth'
                }
        honey_logging.stash.info('logstash-honey', extra=data)
        return SSHFactory.getService(self, transport, service)


def _create_private_and_public_keys():
    private_key = keys.Key.fromString(data=CONFIG['pem_key'])
    public_key = keys.Key.fromString(data=CONFIG['pub_key'])

    return (private_key, public_key)


def _get_and_setup_factory(checker, portal):
    '''
    creates and adds sshkeys and portal to factory
    '''
    factory = HoneyFactory()
    (private_key, public_key) = _create_private_and_public_keys()
    factory.privateKeys = {'ssh-rsa': private_key}
    factory.publicKeys = {'ssh-rsa': public_key}
    factory.portal = portal
    return factory


def ip_to_location(ip):
    r = requests.get('http://freegeoip:8080/json/%s' % ip)
    return r.json()


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
    honey_logging.console.info('Creating checker')
    checker = _get_checker()
    honey_logging.console.info('Creating portal')
    portal = _get_portal(checker)
    honey_logging.console.info('Setting up factory')
    factory = _get_and_setup_factory(checker, portal)
    reactor.listenTCP(CONFIG['port'], factory)
    honey_logging.console.info('Starting up')
    reactor.run()
