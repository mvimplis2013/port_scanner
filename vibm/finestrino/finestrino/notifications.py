import logging
import socket
import sys
import textwrap

import finestrino.task
import finestrino.parameter

logger = logging.getLogger("finestrino-interface")
DEFAULT_CLIENT_email = "finestrino-client@%s" % socket.gethostname()