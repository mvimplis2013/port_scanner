from ..utils.ifconfig_linux import IFConfigCommand, IFConfigParser

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