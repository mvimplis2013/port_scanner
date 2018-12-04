""" 
Implementation of REST interface between the workers and the server.
The "rpc.py" implements the client side of it, and 
The "server.py" implements the server side.
"""
class RemoteScheduler(object):
    """ 
    Scheduler proxy object. Thalks to a RemoteSchedulerResponder.
    """
    def __init__(self, url='http://localhost:8082/', connect_timeout=None):
        pass 
     