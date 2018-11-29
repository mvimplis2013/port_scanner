# Global variables
__version__ = '0.0.1_beta'
nmap_version = 'X.Y.Z_delta'
__author__  = 'Miltos K. Vimplis'

from finestrino.main import FinestrinoMain

def start(config, args):
    global mode

def main():
    """Main entry point for VLAB

    Select the mode (standalone, client or server)
    && Run it ...
    """

    # Share global var
    global core

    # Create the VLAB main instance
    core = FinestrinoMain()
    config = core.get_config()
    args = core.get_args()

    # VLAB-Buster can be ran in Standalone, Client or Server mode
    start(config=config, args=args)

from finestrino import task
from finestrino.task import Task, Config, ExternalTask

from finestrino import parameter
from finestrino.parameter import (
    Parameter, BoolParameter, IntParameter, FloatParameter, DateParameter, DateHourParameter,
    TimeDeltaParameter,
)

from finestrino.interface import run, build

__all__ = [
    'task', 'Task', 'Config', 'ExternalTask', 'Parameter', 'BoolParameter', 'IntParameter', 'FloatParameter',
    'DateParameter', 'DateTimeParameter', 'TimeDeltaParameter',
    'build', 'run',
]