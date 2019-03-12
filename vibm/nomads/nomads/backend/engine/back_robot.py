from . import nomads_logger
from . import TomlParser
from . import DatabaseManager
from . import Scheduler

class BackRobot(object):
    """
    BackRobot operation depends on:
     external configuration for actions frequencies, 
     database tables for targets info and 
     scheduler for actions timing. 
    """
    def __init__(self):
        self.toml_parser = TomlParser.instance()

        self.db_manager = DatabaseManager()
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
        freq_mins = self.toml_parser.get("external-monitoring", "ip-ping-freq-mins")
        nomads_logger.debug( "Frequency Minutes ... %d" % int(freq_mins))

        self.scheduler.scheduleExternalServersPing()



