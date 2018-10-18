import os
import json
import logging.config

__author__ = 'John.Who'

def json_setup_logging(
    default_path='logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
        """
        Setup the logging configuration.


        Keyword Arguments:
            default_path {str} -- the default log configuration file path (default: {'logging.json'})
            default_level {[type]} -- default level to log from (default: {logging.INFO})
            env_key {str} -- SYS ENV key to use for external configuration file path (default: {'LOG_CFG'})
        """
        path = default_path
        value = os.getenv(env_key, None)

        if value:
            path = value
        
        if os.path.exists(path):
            with open(path, 'rt') as f:
                config = json.load(f)

            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)

