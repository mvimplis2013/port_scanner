class NMapPingResponse(object):
    def __init__(self, response_text):
        self.response_text = response_text

    def is_host_up(self):
        lines = self.response_text.split("\n")
        return lines[3]

class NMapPingResponseWithPortsScan(NMapPingResponse):
    def __init__(self):
        pass