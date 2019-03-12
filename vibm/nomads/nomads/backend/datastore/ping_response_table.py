from sqlalchemy import Table, MetaData, Column, Integer, String, Boolean, DateTime
from sqlalchemy import ForeignKey

"""
Table to store responses of mmap ping to external servers.
"""
class PingResponseTable(object):
    def __init__(self):
        self.metadata = MetaData()
        
        self.table = Table( 'ping_responses', self.metadata, 
            Column('id', Integer(), primary_key=True),
            Column('server_id', Integer(), ForeignKey('external_servers.id'))
            Column('dns_name', String(255), index=True),
            Column('ip', String(55)),
            Column('mac_addr', String(255), unique=True),
            Column('is_interesting', Boolean),
            Column('is_up', Boolean),
            Column('last_obesrvation_datetime', DateTime)
        )
