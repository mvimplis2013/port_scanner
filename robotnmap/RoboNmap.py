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
            nmproc = NmapProcess(target)
        else:
            nmproc = NmapProcess(target, '-oN {0}'.format(file_export), safe_mode=False)
        
        rc = nmproc.run()

        if rc != 0:
            raise Exception('EXCEPTION: nmap scan failed: {0}'.format(nmproc.stderr))
        try:
            parsed = NmapParser.parse(nmproc.stdout)
            print parsed
            self.results = parsed
        except NmapParserException as ne:
            print 'EXCEPTION: Exception in Parsing Results: {0}'.format(ne.msg)

    def nmap_all_tcp_scan(self, target, file_export=None):
        ...
        Runs nmap scan against all TCP Ports with version  scanning. 
        Options used are -Pn -sV -p1-65535

        Examples:
        nmap defa
        ...
        target = str(target)

        if file_export == None:
            nmproc = NmapProcess(target, '-p1-65535 -sV')
        else:
            cmd = '-p1-65535 -sV -oN {0}'.format(file_export)
            nmproc = NmapProcess(target, cmd, safe_mode=False)

        rc = nmproc.run()

        if rc != 0:
            raise Exception('EXCEPTION: nmap scan failed: {0}'.format(nmproc.stderr)
        try:
            parsed = NmapParser.parse(nmproc.stdout)
            print parsed
            self.results = parsed
        except NmapParserException as ne:
            print 'EXCEPTION: Exception in Parsing results: {0}'.format(ne.msg)

    def nmap_specific_udp_scan(self, target, portlist, file_export = None):
        ...
        Runs nmap against specified UDP ports given in the portlist argument
        ...
         
