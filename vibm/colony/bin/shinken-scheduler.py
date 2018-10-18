#!/usr/bin/env python

"""This class is the application in charge of scheduling.
The scheduler listens to the Arbiter for the configuration sent 
through the given port as first argument.
The configuration sent by the arbiter specifies which checks and actions
the scheduler must schedule, and a list of reactionners and pollers to execute them.
When the scheduler is already launched and has its own conf, it keeps on listening the arbiter.
In case the arbiter has a new conf to send, the scheduler is stopped and a new one is created.
"""

import os
import sys
import optparse

def main():
    parse = optparse.OptionParser()

