import schedule
import time
import datetime

from daily_port_scan import handle_port_scan

# ****************************
PORT_SCAN_TIME = "22:30"
PING_FREQ_MINS = 4
# ****************************

# Using the DEFAULT logger and setup console displayed message format
config = {
    'disable_existing_loggers': False,
    'version': 1,
    'formatters': {
        'short': {
            'format': '%(asctime)s %(levelname)s %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'short',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'finestrino': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
import logging 
import logging.config
logging.config.dictConfig( config )

logger = logging.getLogger('finestrino')

def job_port_scan():
    handle_port_scan()
    
def job_ping_gateway():
    logger.debug("Ping IP")

def check_all():
    # Once per day perform .. Port Scan
    schedule.every().day.at( PORT_SCAN_TIME ).do( job_port_scan )

    # Every X minutes check ... Is vlab gateway pingazble ?
    schedule.every( PING_FREQ_MINS ).minutes.do( job_ping_ip )

    # Finished Jobs Scheduling ... Proceed with Run Pendings
    while True:
        schedule.run_pending()
        time.sleep(1)
    
if __name__ == '__main__':
    logger.debug( "Starting External Monitoring of VLAB ..." )

    check_all()