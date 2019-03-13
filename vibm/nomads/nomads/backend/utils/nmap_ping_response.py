class NMapPingResponse(object):
    def __init__(self, response_text):
        self.response_text = response_text

    def is_server_running(self):
        pass


class NMapPingResponseWithPortsScan(NMapPingResponse):
    def __init__(self):
        pass