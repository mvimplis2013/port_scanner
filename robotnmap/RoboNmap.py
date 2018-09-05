import os
from libnmap.process import NmapProcess
from libnmap.parser import NmapParser, NmapParserException
from robot.api import logger

class RoboNmap(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        ...
        Nmap Initialize the API 
        ...
        self.results = None 

    def nmap_default_scan(self, target, file_export = None):
        ...
        Runs a basic nmap scan on nmap`s default 1024 ports. Performs the
        default scan - file export is an optional parameter that exports
        to a txt file with -oN flag

        Examples:
        nmap default scan | target | file_export
        ...

        target = str(target)

        if file_export == None:
            nmproc = NmapProcess(target, '-oN {0}'.format(nmproc.stderr))