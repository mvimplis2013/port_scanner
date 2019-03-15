from sqlalchemy import engine
from sqlalchemy import Table, MetaData, Column, Integer, String, Boolean, DateTime
from sqlalchemy import ForeignKey, CheckConstraint

from ..engine import nomads_logger

TABLE_NAME = "ping_ports_scan"

"""
NMAP-ping runs a ports scan after host-discovery.
This table contains records of listening ports and available services per server.
"""
class PingPortScanTable(object):
    """
    Define the sql-engine that comminicates with underlying database server
    """
    def __init__(self, _connection):
        self._connection = _connection

    """ 
    Table already created and ready for records saving ?
    """
    def check_table_exists(self):
        result_proxy = self._connection.execute(
            "SHOW TABLES LIKE '" + TABLE_NAME + "'"
        )

        records_found = result_proxy.fetchall()
        
        if len(records_found) == 0:
            # Table Not Yet Defined
            return False
        else:
            # Table Alread Defined
            return True

    """ 
    Table not found in database and needs to be created for storing new OPEN-PORT records.
    """
    def create(self):
        metadata = MetaData()
        
        self.my_table = Table( TABLE_NAME, metadata, 
            Column('id', Integer(), primary_key=True),
            Column('server_id', Integer()), #, ForeignKey('external_servers.id')
            Column('port', Integer(), index=True),
            Column('protocol', String(3), CheckConstraint("protocol='tcp' OR protocol='udp'")),
            Column('state', String(5)),
            Column('service', String(50)),
            Column('observation_datetime', DateTime(), nullable=False)
        )

        metadata.create_all( self._connection )

    def save_open_ports(self, _server_id, open_ports_arr, _observation_datetime):
        metadata = MetaData()
        
        self.my_table = Table( TABLE_NAME, metadata, 
            Column('id', Integer(), primary_key=True),
            Column('server_id', Integer()), #, ForeignKey('external_servers.id')
            Column('port', Integer(), index=True),
            Column('protocol', String(3), CheckConstraint("protocol='tcp' OR protocol='udp'")),
            Column('state', String(5)),
            Column('service', String(50)), 
            Column('observation_datetime', DateTime(), nullable=False)
        )

        #nomads_logger.debug("Someone wants to save an open port to db %s!" % open_ports_arr)
        for open_port_str in open_ports_arr:
            open_port_parts = open_port_str.split()
            
            #nomads_logger.debug("Part 1=%s .... Part 2=%s .... Part 3=%s" % \
            #    (open_port_parts[0], open_port_parts[1], open_port_parts[2]))

            port_protocol   = open_port_parts[0]
            _port            = port_protocol.split("/")[0]
            _protocol        = port_protocol.split("/")[1]
            #nomads_logger.debug("Port = %s .. Protocol = %s" % (_port, _protocol))

            _state           = open_port_parts[1]
            _service         = open_port_parts[2]

            _insert = self.my_table.insert().values(
                server_id=_server_id,
                port=_port,
                protocol=_protocol,
                state=_state,
                service=_service,
                observation_datetime=_observation_datetime
            )

            result = self._connection.execute( _insert )

            #assert result.inserted_primarry_key == [1]
        
        select_all = self.my_table.select()
        result_proxy = self._connection.execute( select_all )
        results_all = result_proxy.fetchall()

        nomads_logger.debug( "Number of Records in Open Ports Table after Insert for Server ... %d" % \
            len( results_all ))

        return


    def get_ports_open(self):
        pass



