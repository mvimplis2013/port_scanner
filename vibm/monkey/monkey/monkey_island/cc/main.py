#!/home/miltos/anaconda3/bin/python

import os
import sys
import time
import logging

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_PATH not in sys.path:
    sys.path.insert(0, BASE_PATH)

from cc.island_logger import json_setup_logging
json_setup_logging(default_path='.\\monkey_island\\cc\\island_logger_default_config.json', default_level=logging.DEBUG) 
logger = logging.getLogger(__name__)

from cc.app import init_app
from cc.utils import local_ip_addresses
from cc.environment.environment import env
from cc.database import is_db_server_up

def main():
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop

    mongo_url = os.environ.get('MONGO_URL', env.get_mongo_url())

    while not is_db_server_up(mongo_url):
        logger.info('Waiting for MongoDB server ...')
        time.sleep(1)

    app = init_app(mongo_url)
    if env.is_debug():
        app.run(host='0.0.0.0', debug=True, ssl_context=('monkey_island/cc/server.crt', 'monkey_island/cc/server.key'))
    else:
        #http_server = HTTPServer(
        #    WSGIContainer(app), 
        #    ssl_options ={
        #        'cert_file': os.environ.get('SERVER_CRT', 'monkey_island/cc/server.crt'),
        #        'keyfile': os.environ.get('SERVER_KEY', 'monkey_island/cc/server.key')
        #        }
        #)

        http_server = HTTPServer( WSGIContainer(app) )

        http_server.listen(env.get_island_port())

        logger.info('Monkey Island Server is Running on https://{}:{}'.format(
            local_ip_addresses()[0], env.get_island_port()
        ))

        IOLoop.instance().start()

if __name__ == '__main__':
    main()

