import schedule
import time
import logging 

from nmap_native import NMapNative

SCAN_TIME = "14:30"

#: the IP of vlab we want to check if ping-able
HOST = "vlab1.dyndns.org"
HOST = "conserver-2.res.training"

logger = logging.getLogger( "finestrino" )

def jobA():
    print("I am working ....")

def jobB():
    print("I am outside running ...")
    
def handle_port_scan():
    logger.debug('Hei')
    
    # Use the native NMAP ... Open a subprocess to run a shell script
    native = NMapNative( HOST )            
    native.run()

    # NMAP finished running !
    # Start parsing response:         
    # Number of open ports found
    num_open_ports = native.how_many_ports_open()
    if num_open_ports > 0:
        logger.debug( "Found '%d' Open Ports in Vlab Gateway ...", num_open_ports )
    elif num_open_ports == 0:
        logger.warning( "No Open Ports in VLAB Gateway ... Need to Send Notifications" )

    is_ssh_ready = native.is_tcp_22_open()
    if is_ssh_ready:
        logger.debug( "22/tcp ssh port is open ... Can have a walk inside VLAB" )
    else:
        logger.warning( "SSH Port Not Listening at VLAB Gateway ... Need to Send Notifications" )

