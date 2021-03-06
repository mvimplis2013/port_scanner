from finestrino import six

import finestrino

class InputText(finestrino.ExternalTask):
    """
    This class represents something that was created elsewhere by an external process,
    so all we want to do is to implement the output method. 
    
    Arguments:
        finestrino {[type]} -- [description]
    """
    date = finestrino.DateParameter()

    def output(self):
        """Returns the target output for this task. 
        In this case, it expects a file to be present in the local file system.

        :return the target output for this task 
        """
        return finestrino.LocalTarget(self.date.strftime('/var/tmp/text/%Y-%m-%d.txt'))

class WordCount(finestrino.Task):
    date_interval = finestrino.DateIntervalParameter()

    def requires(self):
        """This task's dependencies:

        * :py:class:`~.InputText`

        :return: list of object (:py:class:`finestrino.task.Task`)
        """
        return [InputText(date) for date in self.date_interval.dates()]

    def output(self):
        """Returns the target output for this task.
        In this case, a successful execution of this task will create a file on the local filesystem.

        :return: the target output for this task. 
        """
        return finestrino.LocalTarget('/var/tmp/text-count/%s' % self.date_interval)

    def run(self):
        """
        1. Count the words for each of the :py:meth:`~.InputText.output()` targets created by :py:class:`~.InputText`
        2. write the count into the :py:meth:`~.WordCount.output` target
        """

        count = {}

        # NOTE: self.input() actually returns an element for the InputText.output() target
        for f in self.input(): # The input() method is a wrapper around requires() that returns Target objects
            for line in f.open('r'): # Target objects are a file system/format abstraction and this will return a file stream object
                for word in line.strip().split():
                    count[word] = count.get(word, 0) + 1

        # output data
        f = self.output().open('w')
        for word, count in six.iteritems(count):
            f.write("%s\t%d\n" % (word, count))
        f.close() # WARNING: file system operations are atomic therefore if you don't close the file you lose all data 

if __name__ == '__main__':
        finestrino.run(['WordCount', '--local-scheduler'])