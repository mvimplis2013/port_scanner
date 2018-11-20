"""The worker communicates with the scheduler and does two(2) things:

1) Sends all tasks that has to be run 
2) Get tasks from the scheduler that should be run

When running in LOCAL mode, the worker tals directly to a 
:py:class:`~finestrino.scheduler.Scheduler` instance.

When we run a central server, the worker will talk to the scheduler using a
:py:class:`~finestrino.rpc.RemoteScheduler' instance.
"""

import collections
import getpass
import importlib
import logging
import multiprocessing
import os
import signal
import subprocess
import sys
import contextlib

try:
    import Queue
except ImportError:
    import queue as Queue

import random
import socket
import threading
import time
import traceback
import types

from finestrino import six
