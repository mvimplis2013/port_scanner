from __future__ import print_function

import os 
import time 
import datetime

import logging 

import finestrino 

from .nmap_python import PortScanner

from .nmap_native import SCAN_UDP

from finestrino.parameter import DateMinuteParameter

logger = logging.getLogger( "finestrino-interface" )

#: the full-name of file used for history saving 
HISTORY = "/tmp/vlab/"

#: How often the tool will examine vlab connectablity 
FREQ_mins = 1
FREQ_secs = FREQ_mins * 60

#: How long will be the monitoring session
RANGE = 1

class CreateStatusData(finestrino.Task):
    task_namespace = "examples"

    def collectPingData(self):
        print("Inside collectPingData")
        response = os.system( "ping -c 1 " + HOST )
        print("Response is ... " + str(response))
        
        status = "Vlab Ping: "
        if response == 0:
            # HOST is up 
            status = "%s is up!" % HOST
        else:
            # HOST is down 
            status = "%s is down!" % HOST

        return [response, status]
        
    def run(self):
        response_all = "! "
        for i in range(  RANGE ):
            """
            Hostname or IP Pinging
            """
            time.sleep( FREQ_secs )
            [response, status] = self.collectPingData()
            print(" +++ " + str(response))
            print(" --- " + status )

            response_all += str(response) + " ... " + status

            
            """
            Port Scanning 
            """
            ps = PortScanner()
            response = ps.scan()
            
        with self.output().open('w') as fout:
            fout.write("VLAB External Perimeter Patrol Report ... " + HOST)
            fout.write("\n")
            fout.write( response_all + "\n" )

    def output(self):
        return finestrino.LocalTarget( path = HISTORY + "ping-" + datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S") )

class EntryPoint( finestrino.Task ):
    task_namespace = "examples"

    def run(self):
        print("Running EntryPoint")

    def requires(self):
        return CreateStatusData()
        