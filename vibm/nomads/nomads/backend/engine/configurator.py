from . import nomads_logger

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
        self.ext_vlabs = self.toml_parser.get("external-monitoring", "vlabs")
        #self.external_monitoring_configD.set_watch_vlabs( vlabs )

        self._ips = self.toml_parser.get("external-monitoring", "ips")

        self.ip_ping_freq = self.toml_parser.get("external-monitoring", "ip-ping-freq-mins")
        #self.external_monitoring_configD.set_ip_ping_freq( ip_ping_freq )

        port_scan_freq = self.toml_parser.get("external-monitoring", "port-scan-freq-mins")

        @property
        def external_vlabs(self):
            return self.ext_vlab

        @property
        def ext_ips(self):
            return self._ips

        @property
        def ip_ping_freq_mins(self):
            return self.ip_ping_freq

        @property
        def port_scan_freq_mins(self):
            return self.port_scan_freq        

class Configurator(object):
    def __init__(self, tomlParser):
        self.external_monitoring_configurator = ExternalMonitoringConfigurator( tomlParser )
        
    def configureAll(self):
        self.external_monitoring_configurator.configure()
        
    @property
    def external_monitoring(self):
        return self.external_monitoring_configurator
