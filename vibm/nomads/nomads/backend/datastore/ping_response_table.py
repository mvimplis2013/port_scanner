from sqlalchemy import Table, MetaData, Column, Integer, String, Boolean, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import insert

from ..engine import DatabaseManager

from ..engine import nomads_logger

"""
Table to store responses of mmap ping to external servers.
"""
class PingResponseTable(object):
    def __init__(self, server_id, is_up, observation_datetime):
        self.server_id              = server_id
        self.is_up                  = is_up
        self.observation_datetime   = observation_datetime

        self.metadata = MetaData()
        self.table = Table( 'ping_responses', self.metadata, 
            Column('id', Integer(), primary_key=True),
            Column('server_id', Integer(), ForeignKey('external_servers.id')),
            Column('is_up', Boolean()),
            Column('observation_datetime', DateTime())
        )

    def save_record(self):
        ins = self.table.insert().values(
            server_id=self.server_id,
            is_up=self.is_up,
            observation_datetime=self.observation_datetime
        )

        nomads_logger.debug( str(ins) )

        db_manager = DatabaseManager()
        db_manager.establish_connection()

        if !self.check_table_exists(db_manager._connection ):
            nomads_logger.debug("PING_RESPONSES table not found ... Aborting Insert")
            return
        
        table_exists = self.check_table_exists( db_manager._connection )

        result = db_manager._connection.execute( ins )
        db_manager.close_connection()

        nomads_logger.debug( result )

    def check_table_exists(self, _connection):
        result_proxy = _connection.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='ping_responses'"
        )

        nomads_logger.debug( "Result-Proxy = %s" % result_proxy )

        return False




