'''
Creates the logstash logger and links logging with twisted
'''
import logging
import os

from cmreslogging.handlers import CMRESHandler

from twisted.python import log

# Links twisted logging with python logging
_observer = log.PythonLoggingObserver()
_observer.start()
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

# Creates the logger to use to elasticsearch
stash = logging.getLogger('elastic')
host = dict(
    host='elastic',
    port=9200
)
handler_params = dict(
    hosts=[host],
    auth_type=CMRESHandler.AuthType.NO_AUTH,
    es_index_name='honey-pot'
)
elastic_handler = CMRESHandler(**handler_params)
stash.addHandler(elastic_handler)


# Creates logger for local and console
console = logging.getLogger('console')
