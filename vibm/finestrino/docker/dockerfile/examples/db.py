from datetime import datetime

from sqlalchemy import create_engine, MetaData, Column 
from sqlalchemy_utils import database_exists

USER = "tarzan"
PASS = "jane"

HOST = "vlab-mysql"

DB_NAME = "vlab"

class DataAccessLayer(object):
    connection_string = "mysql+pymysql://" + USER + ":" + PASS + "@" + HOST + "/"

    metatadata = MetaData()

    def db_init(self, connection_string=None):
        self.engine = create_engine(connection_string or self.connection_string)
        self.connection = self.engine.connect()

    @property
    def db_name(self, name):
        self.db_name = name


