from __future__ import print_function

from collections import defaultdict

from finestrino import six

import finestrino

from finestrino.contrib.ssh import RemoteContext, RemoteTarget

from finestrino.mock import MockTarget

SSH_HOST = "some.accessible.host"


class CreateRemoteData(finestrino.Task):
    """ 
    Dump info on running processes on remote host.
    Data is still stored on the remote host.
    """

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on a remote server using the SSH.

        :return: the target output for this task.
        :rtype: object (:py:class:`~finestrino.target.Target`)
        """
        return RemoteTarget(
            "/tmp/stuff",
            SSH_HOST
        )

    def run(self):
        remote = RemoteContext(SSH_HOST)
        print(remote.check_output([
            "ps aux > {0}".format(self.output().path)
        ]))

class ProcessRemoteData(finestrino.Task):
    """ 
    Create a toplist of users based on how many running processes they have on a remote machine.

    In this example the processed data is stored in a Mock Target.
    """
    def requires(self):
        """
        This task's dependencies are:

        * :py:class:`~.CreateRemoteData`

        :return: object (:py:class:`finestrino.task.Task`)
        """
        return CreateRemoteData()

    def run(self):
        process_per_user = defaultdict(int)

        with self.input().open('r') as infile:
            for line in infile:
                username = line.split()[0]
                process_per_user[username] += 1

            toplist = sorted(
                six.iteritems(process_per_user), 
                key=lambda x: x[1],
                reverse=True,
            )

            with self.output().open('w') as outfile:
                for user, n_processes in toplist:
                    print(n_processes, user, file=outfile)

    def output(self):
        """ 
        Return the target output for this task.

        In this case a successful execution of this task will simulate the creation of a file in a filesystem.
        """

        return MockTarget("output", mirror_on_stderr=True)
