class ExternalServersTable(object):
    def __init__(self, record):
        self._id        = record.id
        self._dns_name  = record.dns_name
        self._ip        = record.ip

    @property
    def id(self):
        return self._id

    @property
    def dns_name(self):
        return self._dns_name

    @property
    def ip(self):
        return self._ip

    def __str__(self):
        return "Hello World from External Server with ID = %d" % self._id