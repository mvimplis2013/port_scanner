from sqlalchemy import Table, MetaData, Column, Integer, String, Boolean, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import insert, select

from ..engine import DatabaseManager

from ..engine import nomads_logger

import datetime

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
            Column('server_id', Integer()),  # , ForeignKey('nomads.external_servers.id') 
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

        self._connection = db_manager._connection

        table_exists = self.check_table_exists()

        if not table_exists:
            # Table Not Found ... create it 
            nomads_logger.debug("PING_RESPONSES table not found ... Ready to create it")
            self.create_table()
            
        result = self._connection.execute( ins )
        db_manager.close_connection()

        nomads_logger.debug( result )

    def check_table_exists(self):
        result_proxy = self._connection.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='ping_responses'"
        )

        select_count = result_proxy.fetchone()

        count = select_count[0]

        if count == 1:
            # Table Found
            return True
        else:
            return False

    def create_table(self):
        self.metadata.create_all( self._connection )
        nomads_logger.debug("Table PING_RESPONSES is Created")

    def collect_data_for_period(self, _connection, _from, _to):
        nomads_logger.debug("Select Ping Responses for Period ... %s - %s" % (_from, _to))
        _select = select( [self.table] ).where( self.table.c.observation_datetime < datetime.datetime.now() )

        result_proxy = _connection.execute( _select )

        nomads_logger.debug( "Records Found in PING_RESPONSES ... %d" % ( len(result_proxy.fetchall()) ))






