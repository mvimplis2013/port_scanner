import pytest 

from db import DataAccessLayer

@pytest.fixture(scope='module', autouse=True)
def database():
    dal = DataAccessLayer()
    dal.db_init()
