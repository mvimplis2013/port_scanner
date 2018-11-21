import argparse
from contextlib import contextmanager
#from finestrino.task_register import Register
import sys

class CmdlineParser(object):
    _instance = None

    @classmethod
    def get_instance(cls):
        return cls._instance

    