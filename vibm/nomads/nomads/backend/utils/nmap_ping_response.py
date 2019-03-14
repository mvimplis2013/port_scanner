import re

_HOST_LINE = 2

class NMapPingResponse(object):
    def __init__(self, response_text):
        self.response_text = response_text

    def is_host_up(self):
        # Find the line with host status
        lines = self.response_text.split("\n")
        host_status_line = lines[ _HOST_LINE ].strip()

        _host_is_up = re.search(host_status_line, "host is up", re.IGNORECASE)

        if _host_is_up:
            return True
        else:
            return False

class NMapPingResponseWithPortsScan(NMapPingResponse):
    def __init__(self):
        pass