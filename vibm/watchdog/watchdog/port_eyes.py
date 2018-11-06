import os
from libnmap.process import NmapProcess
from libnmap.parser import NmapParser, NmapParserException
from robot.api import logger

import argparse

class port_eyes(object):
    def __init__(self):
        self.results = None

    def nmap_default_scan(self, target, file_export = None):
        target = str(target)

        if file_export == None:
            nmproc = NmapProcess(target, "-Pn -sV")
        else:
            nmproc = NmapProcess(target, '-oN {0}'.format(file_export),
                                 safe_mode = False)

        rc = nmproc.run()
        
        if rc != 0:
            raise Exception(
                'EXCEPTION: nmap scan failed: {0}'.format(nmproc.stderr))

        try:
            parsed = NmapParser.parse(nmproc.stdout)

            self.results = parsed

            self.nmap_print_results()
        except NmapParserException as ne:
            print('EXCEPTION: Exception in Parsing results: {0}'.format(ne.msg))

    def nmap_all_tcp_scan(self, target, file_export = None):
        print('AAAA')

        target = str(target)

        if file_export == None:
            nmproc = NmapProcess(target, '-p1-65535 -sV')
        else:
            cmd = '-p1-65535 -sV -oN {0}'.format(file_export)
            nmproc = NmapProcess(target, cmd, safe_mode = False)

        rc = nmproc.run()

        if rc != 0:
            raise Exception(
                'EXCEPTION: nmap scan failed: {0}'.format(nmproc.stderr))

        try:
            parsed = NmapParser.parse(nmproc.stdout)
            print(parsed)

            nmap_print_results(this)

            self.results = parsed
        except NmapParserException as ne:
            print('EXCEPTION: Exception in Parsing results: {0}'.format(ne.msg))

    def nmap_specific_udp_scan(self, target, portlist, file_export = None):
        target = str(target)

        if file_export == None:
            nmproc = NmapProcess(target, '-p1-65535 -sV')
        else:
            cmd = '-sU -sV -p {0} -oN {1}'.format(portlist, file_export)
            nmprocess = NmapProcess(target, cmd, safe_mode = False)

        rc = nmprocess.run()

        if rc != 0:
            raise Exception('EXCEPTION: nmap scan failed: {0}'.format(
                nmprocess.stderr))

        try:
            parsed = NmapParser.parse(nmprocess.stdout)
            print(parsed)

            self.results = parsed
        except NmapParserException as ne:
            print('EXCEPTION: Exception in parsing results: {0}'.format(ne.msg))

    def nmap_os_services_scan(self, target, portlist=None, version_intense=0,
                              file_export=None):
        target = str(target)

        if portlist:
            nmap_proc_cmd = '-Pn -sV --version_intensity {0} -p {1}'.format(
                portlist, version_intense)
        else:
            nmap_proc_cmd = '-Pn -sV --version_intensity {0}'.format(
                version_intense)

        if file_export:
            nmap_proc_cmd += " -oN {0}".format(file_export)

        nmproc = NmapProcess(target, cmd, safe_mode=False)

        rc = nmprocess.run()

        if rc != 0:
            raise Exception('EXCEPTION: nmap scan failed: {0}'.format(
                nmprocess.stderr))

        try:
            parsed = NmapParser.parse(nmprocess.stdout)
            print(parsed)

            self.results = parsed
        except NmapParserException as ne:
            print('EXCEPTION: Exception in parsing results: {0}'.format(ne.msg))

    def nmap_script_scan(self, target, portlist=None, version_intense='0',
                        script_name=None, file_export=None):
        target = str(target)

        if portlist and script_name:
            nmap_proc_cmd = "-Pn -sV --version_intensity {0} --script={1} -p {2}".format(
                version_intense, script_name, portlist)
        elif portlist and not script_name:
            nmap_proc_cmd ="-Pn -sV --version_intensity {0} -sC -p {1}".format(
                version_intense, portlist)
        elif script_name and not portlist:
            raise Exception("EXCEPTION: If you use specific script, you have to specify a port")
        else:
            nmap_proc_cmd ="-Pn -sV --version_intensity {0} -sC".format(
                version_intense)

        if file_export:
            nmap_proc_cmd += " -oN {0}".format(file_export)

        nmproc = NmapProcess(target, nmap_proc_cmd, safe_mode = False)
        rc = nmproc.run()

        if rc != 0:
            raise Exception('EXCEPTION: nmap scan failed: {0}'.format(
                nmproc.stderr))

        try:
            parsed = NmapParser.parse(nmproc.stdout)
            print(parsed)

            self.results = parsed
        except NmapParserException as ne:
            print('EXCEPTION: Exception in parsing results: {0}'.format(ne.msg))
    
    def nmap_print_results(self):
        for scanned_hosts in self.results.hosts:
            
            for serv in scanned_hosts.services:
                pserv = "{0:5s}/{1:3s} {2:12s} {3}".format(
                    str(serv.port), str(serv.protocol),
                    str(serv.state),str(serv.service))

                if len(serv.banner):
                    pserv += " ({0})".format(serv.banner)

                if serv.scripts_results:
                    for output in serv.scripts_results:
                        logger.info("\t Output: {0}, Elements: {1}, ID: {2}".
                                    format(output['output'], output['elements'],
                                           output['id']))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    args = parser.parse_args() 

    target = args.target

    porteyes = port_eyes()
    porteyes.nmap_default_scan(target=target)

if __name__ == "__main__":
    main()



        
        



