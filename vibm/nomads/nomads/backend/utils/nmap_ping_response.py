_HOST_LINE = 2

class NMapPingResponse(object):
    def __init__(self, response_text):
        self.response_text = response_text

    def is_host_up(self):
        # Find the line with host status
        lines = self.response_text.split("\n")
        host_status_line = lines[ _HOST_LINE ].trim()

        return host_status_line

class NMapPingResponseWithPortsScan(NMapPingResponse):
    def __init__(self):
        pass