from . import nomads_logger
from . import TomlParser

try: 
    from . import Scheduler
except ImportError:
    print("Must be in GUI Running Mode !")

class BackRobot(object):
    """
    BackRobot operation depends on:
     external configuration for actions frequencies, 
     database tables for targets info and 
     scheduler for actions timing. 
    """
    def __init__(self):
        self.toml_parser = TomlParser.instance()
        self.scheduler = Scheduler()

    """
    Starts all monitoring mechanisms external and internal.
    """
    def start_monitoring(self):
        self.watch_external_servers()

    """
    Watch external servers like a server that is not responding now ... waiting when will be alive again.
    """
    def watch_external_servers(self):
        # How Often the Scheduler will Run the External Servers Alive Test 
        freq_mins = self.toml_parser.get("external-monitoring", "ip-ping-freq-mins")
        self._freq_mins = int( freq_mins )

        print( "Scheduler will Ping External Servers Every '%d' minutes" % self._freq_mins )
        
        self.scheduler.scheduleExternalServersPing( self._freq_mins )

    @property
    def freq_mins(self):
        return self._freq_mins




