from .base_job import BaseJob

"""
This job is responsible for checking the availability of external servers and 
sending notifications in periods that servers are not responding.
""" 
class FollowExternalServer(BaseJob):
    def __init__(self, server_name):
        self.server_name = server_name
