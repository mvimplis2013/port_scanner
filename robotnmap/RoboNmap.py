import os
from libnmap.process import NmapProcess
from libnmap.parser import NmapParser, NmapParserException
from robot.api import logger

class RoboNmap(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        '''
        Nmap Initialize the API 
        '''
        self.results = None 

    def nmap_default_scan(self, target, file_export = None):
        '''
        Runs a basic nmap scan on nmap`s default 1024 ports. Performs the
        default scan - file export is an optional parameter that exports
        to a txt file with -oN flag

        Examples:
        nmap default scan | target | file_export
        '''

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
            print(parsed)
            self.results = parsed
        except NmapParserException as ne:
            print('EXCEPTION: Exception in Parsing Results: {0}'.format(ne.msg))

    def nmap_all_tcp_scan(self, target, file_export=None):
        '''
        Runs nmap scan against all TCP Ports with version  scanning. 
        Options used are -Pn -sV -p1-65535

        Examples:
        nmap defa
        '''

        target = str(target)

        if file_export == None:
            nmproc = NmapProcess(target, '-p1-65535 -sV')
        else:
            cmd = '-p1-65535 -sV -oN {0}'.format(file_export)
            nmproc = NmapProcess(target, cmd, safe_mode=False)

        rc = nmproc.run()

        if rc != 0:
            raise Exception('EXCEPTION: nmap scan failed: {0}'.format(nmproc.stderr))
        try:
            parsed = NmapParser.parse(nmproc.stdout)
            print(parsed)
            self.results = parsed
        except NmapParserException as ne:
            print('EXCEPTION: Exception in Parsing results: {0}'.format(ne.msg))

    def nmap_specific_udp_scan(self, target, portlist, file_export = None):
        '''
        Runs nmap against specified UDP ports given in portlist argument

        Arguments: 
          - ``target`` ... IP or the range of IPs that need to be tested  
          - ``portlist`` ... list of ports, range of ports that need to be tested
                             either comma separated or hyphen 
          - ``file_export`` ... is an optional parameter the exports findings into a file

        Examples:
          nmap_specific_udp_scan <target> <portlist> <file-export>
        '''

        target = str(target)

        if file_export == None:
            nmproc = NmapProcess(target, '-p1-65535 -sV')
        else:
            cmd = '-sU -sV -p {0} -oN {1}'.format(portlist, file_export)
            nmproc = NmapProcess(target, cmd, safe_mode=False)

        rc = nmproc.run()
        if rc != 0:
            raise Exception('EXCEPTION: nmap scan failed: {0}'.format(nmproc.stderr))
        try: 
            parsed = NmapParser.parse(nmproc.stdout)
            print(parsed)
            self.results = parsed
        except NmapParserException as ne:
            print('EXCEPTION: Exception in parsing results {0}'.format(ne.msg))

    def nmap_os_services_scan(self, target, portlist=None, version_intense = 0, file_export = None):
        '''
        Runs 
        Arguments:
            - ``target``: IP or range of IPs that need to be tested
            - ``portlist``: list of ports, range of ports that need be tested
            - ``version_intense``: Version intensity of OS detection
            - ``file_export``: is an optional parameter to export output into a file
        Examples:
            nmap_os_services_scan <target> <port_list> <version_intense> <file_export>
        '''
        target = str(target)

        if portlist:
            nmap_proc_cmd = "-Pn -sV --version-intensity {0} -p {1}".format(portlist, version_intense)
        else:
            nmap_proc_cmd = "-Pn -sV --version-intensity {0}".format(portlist)

        if file_export:
            nmap_proc_cmd += "-oN {0}".format(file_export)

        nmproc = NmapProcess(target, nmap_proc_cmd, safe_mode=False)
        rc = nmproc.run()

        if rc != 0:
            raise Exception('EXCEPTION: nmap scan failed: {0}'.format(nmproc.stderr))
        try: 
            parsed = NmapParser.parse(nmproc.stdout)
            print(parsed)
            self.result = parsed
        except NmapParserException as ne:
            print('EXCEPTION: Exception in parsing results: {0}'.format(ne.msg))

    def nmap_script_scan(self, target, portlist = None, version_instense = "0", script_name = None, file_export = None):
        '''
        Runs nmap with the -sC argument or the --script if script_name is provided

        Arguments:
            - ``target`` ... IP or range of IPs that need to be tested
            - ``portlist`` ... list of ports or range
            - ``version_intense`` ... version intensity of OS detection
            - ``script_name`` ... which script to run
            - ``file_export`` ... whether to use a txt file for output
        Example:
            nmap_script_scan <target> <portlist> <version_intense> <script_name>
        '''

        target = str(target)

        if portlist and script_name: 
            nmap_proc_cmd = "-Pn -sV --version-intensity {0} --script = {1} -p {2}".format(version_intense, script_name, portlist) 
        elif portlist and not script_name:
            nmap_proc_cmd = "-Pn -sV --version-intensity {0} -sC -p {1}".format(version_intense, portlist)         
        elif script_name and not portlist:
            raise Exception('EXCEPTION: If you use specific script need to specify a port')
        else:
            nmap_proc_cmd = "-Pn -sV --version_intensity {0} -sC".format(version_intense)

        if file_export:
            nmap_proc_cmd += " -oN {0}".format(file_export)

        nmproc = NmapProcess(target, nmap_proc_cmd, safe_mode=False)
        rc = nmproc.run()
        if rc != 0:
            raise Exception('EXCEPTION: nmap scan failed: {0}'.format(nmproc.stderr))
        try:
            parsed = NmapParser.parse(nmproc.stdout)
            print(parsed)
            self.results = parsed
        except NmapParserException as ne:
            print('EXCEPTION: Exception in parsing results: {0}'.format(ne.msg))

    def nmap_print_results(self):
        '''
        Retrieves the results of the most recent scan

        Example:
            nmap_print_results
        '''

        print('Hello World')
    
        for scanned_hosts in self.results.hosts:
            logger.info(scanned_hosts)
            logger.info("   PORT    STATE   SERVICE")
            for serv in scanned_hosts.services:
                pserv = "{0:>5s}/{1:3s} {2:12s} {3}".format(
                    str(serv.port),
                    serv.protocol,
                    serv.state,
                    serv.service
                )

                if len(serv.banner):
                    pserv += " ({0})".format(serv.banner)

                print(pserv)

                if serv.scripts_results:
                    for output in serv.scripts_results:
                        print("\t Output: {0}, Elements: {1}, ID: {2}".format(
                            output['output'], output['elements'], output['id']
                        )) 
