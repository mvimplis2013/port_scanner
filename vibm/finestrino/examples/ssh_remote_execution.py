from __future__ import print_function

from collections import defaultdict

from finestrino import six

import finestrino

class CreateRemoteData(finestrino.Task):
    """
    Dump info on running processes on remote host.
    Data is still cerated on the remote host.
    """

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on a remote server using SSH.

        :return: the target output for this task. 
        """
        return RemoteTarget("/tmp/stuff", SSH_HOST)

    def run(self):
        remote = RemoteContext(SSH_HOST)
        print( remote.check_output( [
            "ps aux >".format(self.output().path)
        ]))

class ProcessRemoteData(finestrino.Task):
    """ 
    Creates a toplist of users based on how many processes they have on a remote machine.

    In this example the processed data is stored in a MockTarget.   
    """ 
    def requires(self):