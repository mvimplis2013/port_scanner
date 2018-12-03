from finestrino import __version__, nmap_version

import argparse 

from finestrino.configuration.config import Config

class FinestrinoMain(object):

    # Examples of use
    example_of_use = """
    """

    def __init__(self):
        """Manage Command Line Arguments
        
        Arguments:
            object {[type]} -- [description]
        """
        self.args = self.parse_args()

    def init_args(self):
        version = "Finestrino v" + __version__ + " with nmap v" + nmap_version

        parser = argparse.ArgumentParser(
            prog='finestrino',
            conflict_handler='resolve',
            formatter_class = argparse.RawDescriptionHelpFormatter,
            epilog=self.example_of_use
        )

        return parser

    def parse_args(self):
        """Parse command line arguments
        """
        args = self.init_args().parse_args()

        # Load the configuration file, if it exists
        #self.config = Config(args.conf_file) 

    def get_config(self):
        """Return configuration file object.
        """
        #return self.config

    def get_args(self):
        return self.args
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
    def start(config, args):
        """Start VLAB-Buster
        
        Arguments:
            config {[type]} -- [description]
            args {[type]} -- [description]
        """

        # Load mode
        global mode

        if core.is_standalone():
            from finistrino.standalone import VLABStandalone as VLABMode



