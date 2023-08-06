import configparser

from os import path, environ
from .errors import InvalidConfigSectionError, InvalidConfigOptionError

CONFIG_SEARCH_PATHS = [
    '/etc/glartifacts/glartifacts.conf',
    '$HOME/.config/glartifacts/glartifacts.conf',
    ]

ENV_OVERRIDES = {
    'GLARTIFACTS_DBNAME': ('postgres', 'dbname'),
    'GLARTIFACTS_DBUSER': ('postgres', 'user'),
    'GLARTIFACTS_DBHOST': ('postgres', 'host'),
    'GLARTIFACTS_DBPORT': ('postgres', 'port'),
    'GLARTIFACTS_GITALYADDR': ('gitaly', 'address'),
    }

def _merge_config_file(target, source_path):
    source = configparser.ConfigParser()
    source.read(source_path)

    _merge_config(target, source, source_path)

def _merge_config(target, source, source_path=''):
    for section in source:
        if not section in target:
            raise InvalidConfigSectionError(
                source_path,
                section
                )

        for option, value in source[section].items():
            if not option in target[section]:
                raise InvalidConfigOptionError(
                    source_path,
                    section,
                    option
                    )
            target[section][option] = value

def env_config():
    env_values = {
        'postgres': {},
        'gitaly': {}
        }

    for envvar_name, config in ENV_OVERRIDES.items():
        option_value = environ.get(envvar_name, '')
        if option_value:
            section, option = config
            env_values[section][option] = option_value

    env = configparser.ConfigParser()
    env.read_dict(env_values)
    return env


def default_config():
    defaults = configparser.ConfigParser()
    defaults.read_dict({
        'postgres': {
            'dbname': 'gitlabhq_production',
            'user': 'gitlab',
            'host': '/var/opt/gitlab/postgresql',
            'port': '5432',
            },
        'gitaly': {
            'address': 'unix:/var/opt/gitlab/gitaly/gitaly.socket',
            }
        })

    return defaults

def load_config():
    current_config = default_config()
    for config_path in CONFIG_SEARCH_PATHS:
        p = path.expandvars(config_path)
        if not path.exists(p):
            continue

        _merge_config_file(current_config, p)

    # Apply overrides from the environment
    _merge_config(current_config, env_config())

    return current_config
