import schedule
import time
import datetime
from . import DatabaseManager
from . import nomads_logger

class Scheduler(object):
    def __init__(self):
        self.db_manager = DatabaseManager()

    def scheduleExternalServersPing(self, ping_freq_mins):
        self.external_servers_ping_freq_mins = ping_freq_mins

        # Which External Servers Should the Monitoring Tool Ping ?
        self.db_manager.esatblish_connection()
        self.db_manager.select_external_targets() 
        
        nomads_logger.debug("Ready to Start Scheduling of External Servers Monitoring ...")

    def schedulePortScanInMins(self):
        pass
