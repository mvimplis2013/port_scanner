import schedule
import time
import datetime

from . import nomads_logger

class Scheduler(object):
    def __init__(self):
        pass

    def scheduleExternalServersPing(self, ping_freq_mins):
        self.external_servers_ping_freq_mins = ping_freq_mins
        nomads_logger.debug("Ready to Start Scheduling of External Servers Monitoring ...")

    def schedulePortScanInMins(self):
        pass
