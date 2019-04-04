import subprocess
import re

import logging

SCAN_TCP = "nmap -sT --top-ports 1000 -v -oG - "
SCAN_UDP = "sudo nmap -sU --top-ports 1000 -v -oG - "

SCAN_TCP_UDP = "sudo nmap -sU -sT "

# NMAP command to ping external server
PING_SERVER = "nmap"

# NMAP command to scan live devices at local network & get MAC addresses
INTERNAL_SCAN_LIVE_DEVICES = "nmap -sP "
INTERNAL_SCAN_MAC_ADDRESSES = "sudo nmap -sn "

OPEN_TCP_SSH = "22/tcp"

logger = logging.getLogger("finestrino-interface")

class NMapNative(object):
    def __init__(self, target_ip="localhost"):
        self.target_ip = target_ip

    def is_tcp_22_open(self):
        if self.result_utf8 is None:
            logger.error("No response to parse")
            raise BaseException("No response to parse")

        return OPEN_TCP_SSH in self.result_utf8

    def how_many_ports_open(self):
        if self.result_utf8 is None:
            logger.error("No response to parse")
            raise BaseException("No response to parse")

        nmap_response_lines = self.result_utf8.splitlines()

        # the lines that define the open ports at target-ip
        self.open_ports_lines = []
        for line in nmap_response_lines:
            if re.search(r"[0-9]{2}/(tcp|udp)", line) and "open" in line:
                self.open_ports_lines.append(line)
                
        # Debug message with open ports found
        logger.debug( "Found %d open ports:", len(self.open_ports_lines) )
        logger.debug( self.open_ports_lines )

        return self.open_ports_lines.__len__()

    def store_open_ports(self):
        pass

    """
    Use NMAP to Ping an External Server and Check if Responding.
    """ 
    def ping_external_server(self):
        self.run( PING_SERVER + " " )
        return self.result_utf8

    def run(self, command_type=SCAN_TCP_UDP):
        result = subprocess.run([command_type + self.target_ip], shell=True, stdout=subprocess.PIPE)
        self.result_utf8 = result.stdout.decode('utf-8')

    @property
    def _result_utf8(self):
        return self.result_utf8