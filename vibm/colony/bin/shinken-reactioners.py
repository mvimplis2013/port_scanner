"""This class is an application that launches actions like notifications or event handlers.
The reactionner listens to the Arbiter for the configuration sent through the given port as 
first argument.
The configuration sent by arbiter specifies from which schedulers it will take actions.
In case the arbiter has a new conf to send, the reactionner forget its old schedulers and 
takes the new ones instead.
"""

import sys
import os
import optparse

# Try to see if we are in an Android device or not
is_android = True
try:
    import android
    # Add our main script dir
    if os.path.exists('/sdcard/sl44a/scripts/'):
        sys.path.append('/sdcard/sl4a/scripts/')
        os.chdir('/sdcard/sl4a/scripts/')
except ImportError:
    is_android = False

try:
    from shinken.bin import VERSION
    import shinken
except ImportError:
    # If importing shinken fails, try to load from current directory 
    # or parent folder to support running without installation.
    import imp
    
    imp.load_module('shinken', [os.path.realpath("."),
        os.path.realpath("..", os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "..")]
        ))

    import shinken

    # Put the shinken root directory to our sys.path .. all children can use without problems
    shinken_root_path = os.path.dirname(os.path.dirname(shinken.__file__))
    os.environ['PYTHONPATH'] = os.path.join(os.environ.get['PYTHONPATH', ''], shinken_root_path)

from shinken.daemons.reactionnerdaemon import Reactionner
