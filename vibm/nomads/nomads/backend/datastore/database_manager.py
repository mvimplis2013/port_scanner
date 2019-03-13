import os

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import select 
from sqlalchemy import Table, Column, Integer, Numeric, String, Boolean, DateTime, MetaData
from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy import insert

# SQLAlchemy-Utils
from sqlalchemy_utils import database_exists, create_database, drop_database

import pymysql 

from .ping_port_scan_table import PingPortScanTable

from .external_servers_table import ExternalServersTable

DB_USER = "root"
DB_NAME = "nomads"

class DatabaseManager(object):
    """
    Check that enough database config data is available for successful connection.
    """
    def __init__(self):
        database_url = os.environ['MARIADB-SERVER']
        
        if database_url is None or not database_url:
            # Database URL not available
            raise Exception("Undefined Database URL .. Cannot proceed !")

        connection_str = "mysql+pymysql://" + DB_USER + "@" + database_url + "/" + DB_NAME

        print("Connection string to database ... %s" % connection_str )

        # SQLAlchemy engine knows the SQL-dialect for used datastore
        self.engine = create_engine( connection_str, pool_recycle = 3600)

        self.metadata = MetaData()
        
        # TABLE --> Ping_Targets
        self.external_servers_tbl = Table( 'external_servers', self.metadata, 
            Column('id', Integer(), primary_key=True),
            Column('dns_name', String(255), index=True),
            Column('ip', String(55)),
            Column('mac_addr', String(255), unique=True),
            Column('is_interesting', Boolean),
            Column('is_up', Boolean),
            Column('last_observation_datetime', DateTime)
        )

        # TABLE --> Scan_Ports
        self.open_ports_tbl = Table( 'open_ports', self.metadata, 
            Column('port_id', Integer, primary_key=True),
            Column('server_id', Integer, ForeignKey('external_servers.id')),
            Column('port_num', Integer),
            Column('protocol', String(3), CheckConstraint("protocol='tcp' OR protocol='udp'")),
            Column('service_name', String(55)),
            Column('is_interesting', Boolean),
            Column('is_up', Boolean),
            Column('last_obesrvation_datetime', DateTime)
        )

        # TABLE -> PING_PORTS_FOUND
        self.ping_ports_found_tbl = PingPortScanTable( self.engine )

    """
    Continue with a fresh copy of NOMADS database.
    """
    def delete_db(self):
        if database_exists( self.engine.url ):
            print("Database '%s' was Found and will be Deleted !" % self.engine.url )
            drop_database( self.engine.url )
        else:
            print("Database '%s' was Not Found and cannot be Deleted !" % self.engine.url )

    """ 
    The monitoring tool needs specific tables to save running-generated data.
    Check that the schema is available and in case nothing found then create it.
    """
    def check_and_create_db(self):
        # Is monitoring-database-schema already created ?
        if database_exists(self.engine.url):
            print("Database Exists ... %s" % self.engine.url)
            return 0
        else:
            print("Ready to Create Database Tables ... %s" % self.engine.url)
            create_database(self.engine.url)
            return 1

    """
    Connect to database before start saving new data and querying old one.
    """ 
    def establish_connection(self):
        self.connection = self.engine.connect()

    """
    Disconnect to database and free-up used resources.
    """
    def close_connection(self):
        self.connection.close()

    """
    Create the necessary tables for storing configuration data of vlab-monitoring.
    """
    def create_config_schema(self):
        # Try to connect to database    
        self.engine.connect()
        print( "DBManager Connected to database ... Ready to start transactions" )

        self.metadata.create_all( self.connection )

    """
    Populate database tables with data.
    """
    def save_data_to_tables(self):
        print( "Ready to Save Data to Tables ..." )
        try:
            print( "First Table is ... External_Servers" )
            insert_server = self.external_servers_tbl.insert().values(
                ip = '192.168.2.3',
                dns_name = "vlab3.dyndns.org",
                is_interesting = True
            )

            result = self.connection.execute(insert_server)
            print( "Finished with Table is ... External_Servers" )
            
            print( "Second Table is ... Open_Ports" )
            insert_port = self.open_ports_tbl.insert().values(
                server_id = 1,
                port_num = 22,
                protocol = 'tcp',
                service_name = 'ssh',
                is_interesting = True
            )

            result = self.connection.execute(insert_port)
            print( "Finished with Table is ... Open_Ports" )
        except Exception as x:
            print(x)

        #assert result.inserted_primary_key == [4]

    """
    Query the database for interesting servers needed to be monitored.
    """
    def select_external_targets(self):
        print( "Ready to read all external targets for monitoring ..." )
        
        selection = select([self.external_servers_tbl])
        result_proxy = self.connection.execute( selection )
        results = result_proxy.fetchall()
        
        external_servers_array = []
        for result in results:
            extServersDAO = ExternalServersTable( result )
            external_servers_array.append( extServersDAO )
            
            #print("Result is %d , %s, %s" % (extServersDAO.id, extServersDAO.dns_name, extServersDAO.ip))
            #print("Result 2 is %s" % extServersDAO)

        #assert list(result_proxy) == []
        print( "Found \"%d\" External Servers" % len(external_servers_array))

        return results

    def get_ping_ports_found_tbl(self):
        return self.ping_ports_found_tbl

"""
#PROTOCOL = "mysql+pymysql://"

USERNAME = "cookiemonster"
PASSWORD = "chocolatechip"

SERVER = "mysql01.monster.internal"
PORT = "????"

DATABASE = "cookies"

engine = create_engine(
    "mysql+pymysql://cookiemonster:chocolatechip@mysql01.monster.internal/cookies", pool_recycle=3600)

from sqlalchemy import Table, Column, Integer, Numeric, String, Metadata

metadata = Metadata()

cookies = Table( 'cookies', metadata, 
    Column('cookie_id', Integer(), primary_key=True),
    Column('cookie_name', String(50), index=True),
    Column('cookie_recipe_url', String(255)),
    Column('cookie_sku', String(55)),
    Column('quantity', Integer()),
    Column('unit_cost', Numeric(12, 2)), # 11 digit long with 2 decimal places 
)

# INSERTING #
from sqlalchemy import insert

ins = cookies.insert().values(
    cookie_name = 'chocolate-chip',
    cookie_recipe_url = "http://some.aweso.me/cookie/recipe.html",
    cookie_sku = "CC01",
    quantity = "12",
    unit_cost = "0.50"
)

connection = engine.connect()
result = connection.execute(ins)
assert result.inserted_primary_key = [1]

ins2 = insert(cookies).values(
    cookie_name = "chocolate_chip",
    cookie_recipe_url = "http://some.aweso.me/cookie/recipe.html",
    cookie_sku = "CC01",
    quantity = "12",
    unit_cost = "0.50",
)

ins3 = cookies.insert()
result3 = connection.execute(
    ins3,
    cookie_name = "chocolate_chip",
    cookie_recipe_url = "http://some.aweso.me/cookie/recipe.html",
    cookie_sku = "CC01",
    quantity = "1",
    unit_cost = "0.75",
)

# Insert Multiple Values
inventory_list = [
    {
        'cookie_name': 'peanut_butter',
        'cookie_recipe_url': 'http://some.aweso.me/cookie/peanut.html',
        'cookie_sku': 'PB01',
        'quantity': '24',
        'unit_cost': '0.25'
    }, {
        'cookie_name': 'oatmeal_regin',
        'cookie_recipe_url': 'http://some.aweso.me/cookie/raisin.html',
        'cookie_sku': 'EWW01',
        'quantity': '100',
        'unit_cost': '1.00'
    }
]

# s12 - Querying 
from sqlalchemy.sql import select 

from src.part1.chapter2.s11_inserting import cookies, connection

selection = select([cookies])

result_proxy = connection.execute(selection)

result = result_proxy.fetchall()

assert list(result_proxy) == []

# Filtering 
# Finding chocolate chips
selection = select([cookies]).where(cookies.c.cookie_name == 'chococolate chip')
result_proxy = connection.execute(selection)
record =  result_proxy.first()
assert record.cookie_name == 'chocolate chip'

selection = select([cookies]).where(cookies.c.cookie_name.like('%chocolate%'))
result_proxy = connection.execute(selection)
records = result_proxy.fetchall()
assert [record.cookie_name for record in records] == ['chocolate chip', 'dark chocolate chip']
"""
