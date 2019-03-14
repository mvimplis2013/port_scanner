from .. import DatabaseManager
from .. import NMapNative
from .. import NMapPingResponse

from .. import nomads_logger

from .base_job import BaseJob

"""
This job is responsible for checking the availability of external servers and 
sending notifications in periods that servers are not responding.
""" 
class FollowExternalServer(BaseJob):
    """
    This is a data-centric application and different containers communicate through a backend database.
    """
    def __init__(self):
        self.db_manager = DatabaseManager()

    """ 
    Read from database the interesting external servers that will be monotored.
    """ 
    def prepare(self):
        # Which External Servers Should the Monitoring Tool Ping ?
        self.db_manager.establish_connection()
        
        self.external_servers_arr = self.db_manager.select_external_targets()
        
        ping_ports_found_tbl = self.db_manager.get_ping_ports_found_tbl()
        ping_ports_found_tbl.check_table_exists()
        
        self.db_manager.close_connection()

    def start(self):
        for server in self.external_servers_arr:
            print("Ready to Ping External Server ... %s" % server)

            # "www.google.com"
            nmap_native = NMapNative( server.dns_name )
            ping_response = nmap_native.ping_external_server()

            nomads_logger.debug( "*** Ping Reponse ***\n%s", ping_response)

            obj_repsonse = NMapPingResponse( ping_response )
            nomads_logger.debug( "Is Host Up ... %r" % obj_repsonse.is_host_up() )

    def stop(self):
        pass


