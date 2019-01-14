from __future__ import print_function

import finestrino 

from finestrino.contrib.ftp import RemoteTarget  

#: the FTP Server 
HOST = "some_host"
#: the username
USER = "user"
#: the password
PWD = "some_password"

class ExperimentTask(finestrino.ExternalTask):
    """
    This class represents something that was created elsewhere by an external process,
    so all we want to do is to implement the output method.
    """
    def output(self):
        """ 
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file that will be created in an FTP Server.

        :return: the target for this task.
        :rtype: object (:py:class:`~finestrino.target.Target`)
        """
        return RemoteTarget("/experiment/output1.txt", HOST, username=USER, password=PWD)

    def run(self):
        """
        The execution of this task will write 4 lines of data on this task's target output.
        """
        with self.output().open('w') as outfile:
            print("data 0 200 10 50 60", file=outfile)
            print("data 1 190 09 52 60", file=outfile)
            print("data 2 200 10 52 60", file=outfile)
            print("data 3 195 01 52 60", file=outfile)

class ProcessingTask(finestrino.Task):
    """ 
    This class represents something that was created elsewhere by an external process,
    so all we want to do is to implement the output method.
    """
    def requires(self):
        """ 
        This task's dependencies:

        * :py:class:`~.ExperimentTask`

        :return: object (:py:class:`finestrino.task.Task`)
        """
        return ExperimentTask()

    def output(self):
        """
        Returns the target output for this task.
        In this case a successful execution will create a file in the local file system.

        :return: the target output for this task.
        :rtype: object (:py:class:`finestrino.target.Target`)
        """
        return finestrino.LocalTarget('/tmp/processdata.txt')

    def run(self):
        avg = 0.0
        elements = 0
        sumval = 0.0

        # Target objects are a file system/format abstraction and this will return a file stream object 
        # NOTE: self.input() actually returns the ExperimentTask.output() target
        for line in self.input().open('r'):
            values = line.split(" ")
            avg += float(values[2])
            sumval += float(values[3])
            elements = elements + 1

        # average 
        avg = sumval / elements

        # save calculated values
        with self.output().open('w') as outfile:
            print(avg, sumval, file=outfile)

if __name__ == "__main__":
    finestrino.run()