import yaml


def _get_config():
    '''
    setups the config from config.yml

    TODO: This should really validate it as well for required parts
    '''
    with open('./config.yml') as config_file:
        text = config_file.read()

    config = yaml.load(text)
    return config

print('Reading config')
CONFIG = _get_config()
