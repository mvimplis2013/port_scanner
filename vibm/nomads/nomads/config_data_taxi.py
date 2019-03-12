import os 

from .backend.datastore.database_manager import DatabaseManager

START_WITH_NEW_DB = True

class ConfigDataTaxi(object):
    """
    Configuration data consists of IPs, Names and Ranges.
    The end-user is interested in specific targets defined in various ways.
    """
    def __init__(self, new_ips, new_names, new_range):
        self.new_ips    = new_ips
        self.new_names  = new_names
        self.new_range  = new_range

        self.db_manager = DatabaseManager()
        
    """
    End-User specified new config data through GUI. 
    The backend-robot must be informed from database. 
    """
    def take_new_data_to_store(self):
        # Step 0 ... Delete old database 
        if START_WITH_NEW_DB:
            print("Ready to delete old database")
            self.start_with_new_db()

        # Step 1 ... Is database available ?
        self.check_terminal()

        # Step 2 ... Establish Connection
        self.gate_open()

        # Step 3 ... Create Schema Tables
        self.prepare_datastore()

        # Step 4 ... Save Data to Tables
        self.save_to_datastore()

        # Step 5 ... Read Data from Tables
        self.get_from_datastore() 

    """
    Mainly for testing purposes, drop old database and create new one.
    New tables, with empty records ready to store monitoring engine output.
    """
    def start_with_new_db(self):
        self.db_manager.delete_db()

    """ 
    Checks whether the database schema with required tables is available.
    In case of first time run and empty datastore the schema is created before sending data.
    """ 
    def check_terminal(self):
        self.db_manager.check_and_create_db()

    """
    In order to start transactions with NOMADS database a connection is needed.
    """
    def gate_open(self):
        self.db_manager.establish_connection()

    """
    Eveythingt is ready {database + connection} proceed with tables creation
    """
    def prepare_datastore(self):
        self.db_manager.create_config_schema()

    """ 
    Ready to save new data to appropriate tables.
    """
    def save_to_datastore(self):
        self.db_manager.save_data_to_tables()

    """
    Read the current list of external servers.
    """
    def get_from_datastore(self):
        self.db_manager.select_external_targets()