import datetime

from .. import TomlParser
from .. import Configurator

from .. import DatabaseManager, TableNotYetCreated

from .. import NMapNative
from .. import NMapPingResponse, NMapPingResponseWithPortsScan

from .. import PingResponseTable, PingPortScanTable

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
        toml_parser = TomlParser.instance()
        self.configurator = Configurator(toml_parser)

        self.db_manager = DatabaseManager()

    """ 
    Read from database the interesting external servers that will be monotored.
    """ 
    def prepare(self):
        # Which External Servers Should the Monitoring Tool Ping ?
        self.db_manager.establish_connection()
        
        self.configurator.configureAll() 
        
    def start(self):
        nomads_logger.debug( "***** New Patrol for External-Server(s) Availability ... %s *****" % (datetime.datetime.now()) )

        _connection = self.db_manager._connection

        # FIRST STEP: Get the list of external servers
        try:
            external_servers_arr = self.db_manager.select_external_targets()
        except TableNotYetCreated as e:
            nomads_logger.warn( "This table has not yet been created ... %s" % e.table_name)
            
            # Wait until external_servers available ?!!
            nomads_logger.debug("Ready to create table and save TOML external-configuration ... 'external_servers'")
            self.db_manager.create_table( [self.db_manager.tbl_external_servers] )

            # Insert TOML defined external-monitoring data
            # ip = '', dns_name = "vlab3.dyndns.org", is_interesting = True
            data = {}
            data["server-ip"] = self.configurator.external_monitoring.ext_ips
            data["dns-name"] = self.configurator.external_monitoring.ext_vlabs
            data["is-interesting"] = True

            self.db_manager.save_data_SERVERS_table(data)
            
        # End of FIRST STEP: List of External-Servers retrieved    

        for server in external_servers_arr:
            print("Ready to Ping External Server ... %s" % server)

            # "www.google.com"
            nmap_native = NMapNative( server.dns_name )
            ping_response = nmap_native.ping_external_server()

            nomads_logger.debug( "*** Ping Reponse ***\n%s", ping_response)

            # Is Host Up and Running ?
            response_host = NMapPingResponse( ping_response )
            _is_host_up = response_host.is_host_up()

            # Which Ports are Open ?
            response_ports = NMapPingResponseWithPortsScan( ping_response )
            open_ports_arr = response_ports.get_open_ports_list()

            # Datetime of host ping
            _now = datetime.datetime.now() 

            nomads_logger.debug( "Is Host Up ... %d / %s - %s" % (server.id, str(_is_host_up), _now) )
            nomads_logger.debug( "For Server '%d' Found (%d) Open Ports !" % (server.id, len(open_ports_arr)) )

            # Save ping-output to database
            out_table = PingResponseTable( _connection )
            out_table.save_record( server.id, _is_host_up, _now )

            # *** Save ports-scan to database ***
            ports_scan_table = PingPortScanTable( _connection )
            ports_table_ok = ports_scan_table.check_table_exists()
        
            if not ports_table_ok:
                # Table Ports Scan Output ... Not Found
                ports_scan_table.create()

            # Save Open-Ports Array for Server
            ports_scan_table.save_open_ports( server._id, open_ports_arr, _now )

            # *** End of ports-scan to database *** 

            out_table.collect_data_for_period( _now, _now )

            #ports_scan = NMapPingResponseWithPortsScan( ping_response )

    def stop(self):
        self.db_manager.close_connection()



