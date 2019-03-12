from . import ExternalMonitoringConfigData
from . import DatabaseConfigData
from . import MessageQueueConfigData

class DatabaseConfigurator(object):
    def __init__(self, toml_parser):
        self.toml_parser = toml_parser
        self.database_configD = DatabaseConfigData() 

class ExternalMonitoringConfigurator(object):
    def __init__(self, toml_parser):
        self.toml_parser = toml_parser
        #self.external_monitoring_configD = ExternalMonitoringConfigData()

    def configure(self):
        self.vlab = self.toml_parser.get("external-monitoring", "vlabs")
        self.external_monitoring_configD.set_watch_vlabs( vlabs )

        ip_ping_freq = self.toml_parser.get("external-monitoring", "ip-ping-freq")
        self.external_monitoring_configD.set_ip_ping_freq( ip_ping_freq )

        ports_scan_freq = self.toml_parser.get()
        

class Configurator(object):
    def __init__(self, tomlParser):
        self.external_monitoring_configurator = ExternalMonitoringConfigurator(self.tomlParser)
        
    def configureAll(self):
        pass
        
    @property
    def external_monitoring(self):
        pass