class ExternalServersTable(object):
    def __init__(self, record):
        self._id                        = record.id
        self._dns_name                  = record.dns_name
        self._ip                        = record.ip
        self._mac                       = record.mac_addr
        self._is_interesting            = record.is_interesting
        self._is_up                     = record.is_up 
        self._last_observation_datetime = record.last_observation_datetime 

    @property
    def id(self):
        return self._id

    @property
    def dns_name(self):
        return self._dns_name

    @property
    def ip(self):
        return self._ip

    @property
    def mac(self):
        return self._mac

    @property
    def is_interesting(self):
        return self._is_interesting

    @property
    def is_up(self):
        return self._is_up

    @property
    def last_observation_datetime(self):
        return self._last_observation_datetime

    def __str__(self):
        return "Externa Servers Table Record with {id=%d, dns=%s, ip=%s, \n mac=%s, is_intersting=%r, is_up=%r, last_observation_dateT=%r}" \ 
            % (self._id, self._dns_name, self._ip, self._mac, self._is_interesting, self._is_up, self._last_observation_datetime)