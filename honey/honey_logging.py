'''
Creates the logstash logger and links logging with twisted
'''
import logstash
import logging

from twisted.python import log


_observer = log.PythonLoggingObserver()
_observer.start()
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

stash = logging.getLogger('python-logstash-logger')
stash.addHandler(logstash.TCPLogstashHandler('logstash', 5000))
