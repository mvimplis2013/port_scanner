from . import nomads_logger

class External(object):
    def __init__(self):
        pass

"""
class ExternalMonitoringConfigData(object):
    def __init__(self):
        pass

    def __init__(self, vlabs=[]):
        self.vlabs = vlabs
        self.ipPingFreq = ""

    @property
    def watch_vlabs(self):
        return self.vlabs

    def set_watch_vlabs(self, vlabs=[]):
        self.vlabs = vlabs

    @property
    def ip_ping_freq(self):
        return self.ip_ping_freq
    
    def set_ip_ping_freq(self, ipPingFreq):
        self.ipPingFreq = ipPingFreq

    def __str__(self):
        return "External Configuration of Monitoring Tool: " + str(self.vlabs) + " , " + self.ipPingFreq 
"""