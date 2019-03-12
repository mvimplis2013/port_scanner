import schedule
import time
import datetime
from . import DatabaseManager
from . import nomads_logger

import schedule
import time

def job():
    print( "Wake up from scheduler" )

class Scheduler(object):
    def __init__(self):
        self.db_manager = DatabaseManager()

    def scheduleExternalServersPing(self, ping_freq_mins):
        self.external_servers_ping_freq_mins = ping_freq_mins

        # Which External Servers Should the Monitoring Tool Ping ?
        self.db_manager.esatblish_connection()
        self.db_manager.select_external_targets() 

        nomads_logger.debug("Ready to Start Scheduling of External Servers Monitoring ...")

        schedule.every(2).minutes.do(job)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def schedulePortScanInMins(self):
        pass
