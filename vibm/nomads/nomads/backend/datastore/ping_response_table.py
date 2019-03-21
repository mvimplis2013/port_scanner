from sqlalchemy import create_engine
from sqlalchemy import Table, MetaData, Column, Integer, String, Boolean, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import insert, select

from .database_manager import DatabaseManager

from nomads.backend.utils.back_logger import nomads_logger

import datetime
import os

"""
Table to store responses of mmap ping to external servers.
"""
class PingResponseTable(object):
    def __init__(self, _connection):
        self._connection = _connection

    def save_record(self, _server_id, _is_up, _observation_datetime):
        table_exists = self.check_table_exists()
        if not table_exists:
            # Table Not Found ... create it 
            nomads_logger.debug("PING_RESPONSES table not found ... Ready to create it")
            self.create_table()
        else:
            self.connect_with_pre_existing_table()
                    
        ins = self.my_table.insert().values(
            server_id=_server_id,
            is_up=_is_up,
            observation_datetime=_observation_datetime
        )
        result = self._connection.execute( ins )
        
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
        metadata = MetaData()

        # Case Create: SELF.MY_TABLE is here !!
        self.my_table = Table( 'ping_responses', metadata, 
            Column('id', Integer(), primary_key=True),
            Column('server_id', Integer()),  # , ForeignKey('nomads.external_servers.id') 
            Column('is_up', Boolean()),
            Column('observation_datetime', DateTime())
        )

        metadata.create_all( self._connection )
        nomads_logger.debug("Table PING_RESPONSES is Created")

    def connect_with_pre_existing_table(self):
        metadata = MetaData()

        # Case Found: SELF.MY_TABLE is here !!
        self.my_table = Table( 'ping_responses', metadata, 
            Column('id', Integer(), primary_key=True),
            Column('server_id', Integer()),  # , ForeignKey('nomads.external_servers.id') 
            Column('is_up', Boolean()),
            Column('observation_datetime', DateTime())
        )

        selection       = self.my_table.select()
        result_proxy    = self._connection.execute( selection )
        results         = result_proxy.fetchall()

    @staticmethod
    def collect_data_for_period(_from, _to):
        nomads_logger.debug("Select Ping Responses for Period ... %s - %s" % (_from, _to))

        database_url = os.environ['MARIADB-SERVER']
        connection_str = "mysql+pymysql://root@" + database_url + "/nomads"
        engine = create_engine( connection_str )
        
        connection = engine.connect()

        result = connection.execute( "select * from external_servers where observation_datetime > {} and observation_datetime < {}".format(_from, _to) )
        for row in result:
            print("datetime:", row['observation_datetime'])
        
        records_found = result.fetchall()
        connection.close()
        
        #result_proxy = connection.execute( _select )
        #records_found = result_proxy.fetchall()

        nomads_logger.debug( "Records Found in PING_RESPONSES ... %d" % len(records_found) )

        return records_found






