import subprocess

import re

COMMAND = "ifconfig"
PARAMS  = "-l"

class Error(Exception):
    pass

class AddressError(Error):
    def __init__(self, message):
        self.message = message

class IFConfigParser(object):
    def __init__(self, response):
        self.response = response

        self.mac_addresses = []
        self.ip_addresses = []

    def get_physical_address(self, mac_text):
        pieces = mac_text.split()
        
        my_mac = pieces[1].strip()
        my_mac = my_mac[:-1]

        #print("-->" + my_mac)

        self.mac_addresses.append(my_mac)

    def get_net_address(self, ip_text):
        pieces = ip_text.split(":")
        
        my_ip = pieces[1].strip()
        
        #print("My Ip is ..." + my_ip)
        
        self.ip_addresses.append( my_ip )

    def find_all_addresses(self, interfaces_text):
        # Create regular expression pattern
        chopMAC = re.compile(r"HWaddr.*?,", re.DOTALL)
        chopIP = re.compile(r"inet addr.*? ", re.DOTALL)
        
        for interface in interfaces_text:
            if len(interface) == 0:
                continue 

            # A long line with details for an interface 
            data_chopped_MAC = chopMAC.search( interface )
            if data_chopped_MAC == None:
                continue
            self.get_physical_address( data_chopped_MAC.group() )
            
            data_chopped_IP = chopIP.search( interface )
            if data_chopped_IP == None:
                continue
            self.get_net_address( data_chopped_IP.group() )
            
            #print( "Interface text is ..." + interface )
            #print( "Interface is ..." + data_chopped_MAC.group() + " / " + data_chopped_IP.group() )

    def parse(self):
        # Chop text between #chop-begin and #chop-end
        lines = self.response.split("\n")
        
        interfaces = []
        pieces = []
        for line in lines:
            # Remove unwanter leading and trailing spaces
            line = line.strip()
            #print("Line is: " + line + "/ length = " + str(len(line)) )

            if len(line) == 0:
                # Found an empty line ... divider between interfaces

                # Merge all lines in this section
                section = ",".join( pieces )
                
                interfaces.append( section )
                
                pieces = []
                continue
            
            # This is a line from an interface data section
            pieces.append( line )

        
        # print( "==> Number of Interfaces Found ... " + str( len(interfaces) ))

        # Find IP & Physical addresses of interfaces
        self.find_all_addresses( interfaces )

    @property
    def _mac_addresses(self):
        return self.mac_addresses

    @property
    def _ip_addresses(self):
        return self.ip_addresses 
        
class IFConfigCommand(object):
    def __init__(self, parameter_list):
        pass

    def run(self, parameter_list):
        pass

    @staticmethod
    def _run():
        result = subprocess.run(
            [COMMAND, PARAMS], 
            shell=True, stdout=subprocess.PIPE)

        return result.stdout.decode('utf-8')