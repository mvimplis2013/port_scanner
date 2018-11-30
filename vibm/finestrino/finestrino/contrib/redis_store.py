import datetime
import logging

from finestrino.Target import Target
from finestrino.parameter import Parameter

logger = logging.getLogger('finestrino-interface')

try:
    import redis
except ImportError:
    logger.warning("Loading redis_store module without redis installed. "
                    "Will crash at runtime if redis_store functionality is used.")

class RedisTarget(Target):
    """ 
    Target for a resource in Redis.
    """                
    marker_prefix = Parameter(default='finestrino', 
        config_path = dict(section='redis', name='marker-prefix'))

    def __init__(self, host, port, db, update_id, password=None,
        socket_timeout=None, expire=None):
        """[summary]
        
        Arguments:
            host {[str]} -- Redis server host
            port {[int]} -- Redis server port            
            db {[int]} -- database index
            update_id {str} -- an identifier for this data hash
        
        Keyword Arguments:
            password {[type]} -- [description] (default: {None})
            socket_timeout {[type]} -- [description] (default: {None})
            expire {[type]} -- [description] (default: {None})
        """
