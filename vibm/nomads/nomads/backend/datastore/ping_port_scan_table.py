from sqlalchemy import engine
from sqlalchemy import Table, MetaData, Column, Integer, String, Boolean, DateTime
from sqlalchemy import ForeignKey, CheckConstraint

"""
NMAP-ping runs a ports scan after host-discovery.
This table contains records of listening ports and available services per server.
"""
class PingPortScanTable(object):
    """
    Define the sql-engine that comminicates with underlying database server
    """
    def __init__(self, engine):
        self.engine = engine

        self.metadata = MetaData()
        
        self.table = Table( 'ping_port_scans', self.metadata, 
            Column('id', Integer(), primary_key=True),
            Column('server_id', Integer(), ForeignKey('external_servers.id')),
            Column('port', Integer(), index=True),
            Column('protocol', String(3), CheckConstraint("protocol='tcp' OR protocol='udp'")),
            Column('state', String(5)),
            Column('service', String(50))
        )

    """ 
    Table already created and ready for records saving ?
    """
    def check_table_exists(self):
        result = self.engine.execute(
            "SHOW TABLES LIKE 'ping-port-scans'"
        )

        print( "Result is ... %s" % result )


