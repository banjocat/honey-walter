import yaml
import sys
import logging

from voluptuous import Schema, MultipleInvalid, Invalid
from voluptuous import Required, All, Range, Length

schema = Schema({
    Required('username', default='root'): All(str, Length(min=1)),
    Required('password', default='password'): All(str, Length(min=1)),
    Required('port'): All(int, Range(min=1, max=65535)),
    Required('motd', default='Hi'): str,
    Required('simple_commands'): dict,
    Required('pem_key'): str,
    Required('pub_key'): str
    })


def _get_config():
    with open('./config/config.yml') as config_file:
        text = config_file.read()

    config = yaml.load(text)
    try:
        schema(config)
    except (MultipleInvalid, Invalid) as e:
        logging.error('Invalid config.yml')
        logging.error(str(e))
        sys.exit(1)
    return config

CONFIG = _get_config()
