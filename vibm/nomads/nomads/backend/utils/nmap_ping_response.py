import re

from ..engine import nomads_logger

_HOST_LINE = 2

_OPEN_PORTS_FROM    = 5

class NMapPingResponse(object):
    def __init__(self, response_text):
        self.lines = response_text.split("\n")
        

    def is_host_up(self):
        # Find the line with host status
        host_status_line = self.lines[ _HOST_LINE ].strip()

        _host_is_up = re.search("host is up", host_status_line, re.IGNORECASE)

        if _host_is_up:
            return True
        else:
            return False

class NMapPingResponseWithPortsScan(object):
    def __init__(self, response_text):
        self.lines = response_text.split("\n")

    def get_open_ports_list(self):
        ports_header = self.lines[ _OPEN_PORTS_FROM ]
        nomads_logger.debug( "Inside NMapPing with Ports Scan Response ... %s" % ports_header)

        return