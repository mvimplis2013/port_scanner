import sys 

import logging

logger = logging.getLogger("finestrino-interface")

try:
    # Import the NMAP module to handle all port-scan requests
    import nmap
except ImportError:
    logger.error("Failed to import PYTHON-NMAP module ... Expecting numerous exceptions during port-scan") 

"""
The Main Class Definition  
"""
class PortScanner(object):
    """
    Initialize PortScanner to know the target entity that will search.
    """
    def __init__(self, address=None, port_range=None):
        # Which address to call/ ping , like "vlab1.dyndns.org" or "127.0.0.1"
        self.address = address
        # Scan a range of ports , like "22-443"
        self.port_range = port_range

        try:
            self.nm = nmap.PortScanner()
            logger.debug("Nmap Found" + str(sys.exc_info()[0]))
        except nmap.PortScannerError:
            logger.error("Nmap not found: " + str(sys.exc_info()[0]))
        except: 
            logger.error("Unexpected error: " + str(sys.exc_info()[0]))
 
    """
    Start port scanning to find the set of up and listening.
    """
    def scan(self):
        if self.nm and self.address and self.port_range:
            # Have a valuable scanner and a reasonable ip target 
            self.nm.scan(self.address, self.port_range)
        else:
            # Error missing the vlab ip-address or port-range.
            # Also make sure that the nmap port-scanner initialization is OK. 
            logger.error("Cannot proceed with port scan ... Define first basic variables !\n" + 
                "NMAP is %s , HOST is %s , PORT is %s", self.nm, self.address, self.port_range)

            return -1
