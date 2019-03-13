import schedule
import time
import datetime

from . import DatabaseManager
from . import PingPortScanTable

from . import nomads_logger
from . import NMapNative

from . import FollowExternalServer

import schedule
import time

class Scheduler(object):
    def __init__(self):
        pass

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
        job_follow_external = FollowExternalServer()
        job_follow_external.start()

        # "www.google.com"
        nmap_native = NMapNative( "mail.cbt-training.de" )
        nmap_native.ping_external_server()






