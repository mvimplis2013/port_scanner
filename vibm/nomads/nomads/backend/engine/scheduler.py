import schedule
import time
import datetime
from . import DatabaseManager
from . import nomads_logger

import schedule
import time

class Scheduler(object):
    def __init__(self):
        self.db_manager = DatabaseManager()

    def scheduleExternalServersPing(self, ping_freq_mins):
        self.external_servers_ping_freq_mins = ping_freq_mins

        nomads_logger.debug("Ready to Start Scheduling of External Servers Monitoring ...")

        schedule.every( ping_freq_mins ).minutes.do( self.job )

        while True:
            schedule.run_pending()
            time.sleep(1)

    def schedulePortScanInMins(self):
        pass

    def job(self):
        # Which External Servers Should the Monitoring Tool Ping ?
        self.db_manager.establish_connection()
        print( self.db_manager.select_external_targets() )
        self.db_manager.check_and_create_db 


