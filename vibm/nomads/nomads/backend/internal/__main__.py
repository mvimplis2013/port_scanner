from ..utils.ifconfig_linux import IFConfigCommand, IFConfigParser
from ..utils.nmap_native import NMapNative, INTERNAL_SCAN_MAC_ADDRESSES

print("Agent is Coming")

response = IFConfigCommand._run()

print( response )

print( "************************************" )

print( response[0:100] )

parser = IFConfigParser(response)
parser.parse()

all_ips = parser._ip_addresses
all_macs = parser._mac_addresses

for ip in all_ips:
    print("IP is ..." + ip)

for mac in all_macs:
    print("MAC is ..." + mac)

#nmap = NMapNative( all_ips[0] + "/24" )
nmap = NMapNative( "192.168.5.5" )
nmap.run( INTERNAL_SCAN_MAC_ADDRESSES )

print( "NMAP -sP -n response is ..." + nmap._result_utf8)
