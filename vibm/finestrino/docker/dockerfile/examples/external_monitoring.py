import schedule
import time
import datetime

from daily_port_scan import handle_port_scan

# ****************************
PORT_SCAN_TIME = "20:17"
PING_FREQ_MINS = 2
# ****************************

logger = logging.getLogger('finestrino')

def job_port_scan():
    handle_port_scan()
    
def job_ping_gateway():
    logger.debug("Ping IP")

def check_all():
    # Once per day perform .. Port Scan
    schedule.every().day.at( PORT_SCAN_TIME ).do( job_port_scan )

    # Every X minutes check ... Is vlab gateway pingazble ?
    schedule.every( PING_FREQ_MINS ).minutes.do( job_ping_gateway )

    # Finished Jobs Scheduling ... Proceed with Run Pendings
    while True:
        schedule.run_pending()
        time.sleep(1)
    
if __name__ == '__main__':
    logger.debug( "Starting External Monitoring of VLAB ..." )

    check_all()