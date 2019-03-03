from sqlalchemy import create_engine
from sqlalchemy.sql import select 
from sqlalchemy import Table, Column, Integer, Numeric, String, MetaData

from sqlalchemy import insert

class DatabaseManager(object):
    def __init__(self):
        engine = create_engine( 
            "mysql+pymysql://root@172.18.0.2/cookies", 
            pool_recycle=3600)

        connection = engine.connect()

        metadata = MetaData()
        
        cookies = Table( 'cookies', metadata, 
            Column('cookie_id', Integer(), primary_key=True),
            Column('cookie_name', String(50), index=True),
            Column('cookie_recipe_url', String(255)),
            Column('cookie_sku', String(55)),
            Column('quantity', Integer()),
            Column('unit_cost', Numeric(12, 2)), # 11 digit long with 2 decimal places 
        )

        metadata.create_all(connection)

        ins = cookies.insert().values(
            cookie_name = 'chocolate-chip',
            cookie_recipe_url = "http://some.aweso.me/cookie/recipe.html",
            cookie_sku = "CC01",
            quantity = "12",
            unit_cost = "0.50"
        )

        #connection = engine.connect()

        result = connection.execute(ins)
        #assert result.inserted_primary_key == [4]
        
        selection = select([cookies])
        result_proxy = connection.execute(selection)
        result = result_proxy.fetchall()
        
        print( result )

        assert list(result_proxy) == []


""" 
PROTOCOL = "mysql+pymysql://"

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