from . import nomads_logger
from . import Scheduler
from . import DatabaseManager

class BackRobot(object):
    def __init__(self):
        self.scheduler = Scheduler

    """
    Starts all monitoring mechanisms external and internal.
    """
    def start_monitoring(self):
        self.watch_external_servers()

    """
    Watch external servers like a server that is not responding now ... waiting when will be alive again.
    """
    def watch_external_servers(self):
        self.scheduler.scheduleExternalServersPing()
        


