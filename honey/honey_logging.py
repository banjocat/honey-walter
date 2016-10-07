'''
Creates the logstash logger and links logging with twisted
'''
import logstash
import logging

from twisted.python import log

# Links twisted logging with python logging
_observer = log.PythonLoggingObserver()
_observer.start()
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

# Creates the logger to use to logstash
stash = logging.getLogger('python-logstash-logger')
stash.addHandler(logstash.TCPLogstashHandler('logstash', 5000))
