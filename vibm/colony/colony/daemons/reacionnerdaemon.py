#!/usr/bin/env python

# This class is an application that launched actions for the schedulers.
# Actions can be: 
#  Notifications 
#  Event Handlers
# 
# When running the Reactionner will:
#   Respond to Pyro pings from Arbiter
#   Listen for new configurations from Arbiter
# 
# The configuration consists of a list of Schedulers for 
# which the Reactionner will launch actions about.

from shinken.satellite import Satellite

