import datetime 
import json 

import finestrino 

from finestrino.contrib.esindex import CopyToIndex

class FakeDocuments(finestrino.Task):
    """
    Generates a local file containing 5 elements of data in JSON format.
    """

    #: the date parameter 
    date = finestrino.parameter.DateParameter(default = datetime.date.today())

    def run(self):
        """
        Writes data in JSON format into the task's output target.

        The data objects have the following attributes:
        *  `_id` is the defauld elastic search field
        * `text`: the text,
        * `date`: the day when the data was created.
        """
        today = datetime.date.today()

        with self.output().open('w') as output:
            for i in range(5):
                output.write(json.dumps({"_id": i, "text": "Hi %s" % i, "date": str(today)}))
                output.write("\n")

    def output(self):
        """
        Returns the target output for this task.
        In this case a successful execution of this task will create a file on local filesystem.

        :return: the target output for this task 
        :rtype object (:py:class:`finestrino.target.LocalTarget`)
        """

        return finestrino.LocalTarget(path="/tmp/_docs-%s.ldj" % self.date)

class IndexDocuments(CopyToIndex):
    """
    This task loads JSON data contained in a :py:class:`finestrino.target.Target` into an ElasticSearch index.

    This task's input will be the target returned by :py:meth:`~.FakeDocuments.output`.

    This class uses :py:meth:`finetsrino.contrib.esinsdex.CopyToIndex.run`.

    After running this task you can run:

    ... code-block:: console
        $>curl "localhost:9200/example_index/_search?pretty"

        to see the indexed documents.
    """
    date = finestrino.parameter.DateParameter()

    #: the name of index in ElasticSearch to be updated
    index = 'example_index'

    #: the name of the document type
    doc_type = 'greetings'

    #: the host running the ElasticSearch service 
    host = 'localhost'

    #: the port used by the ElasticSearch service
    port = 9200

    def requires(self):
        """
        This task's dependencies:

        * :py:class:`~.FakeDocuments`

        :return: object (:py:class:`finestrino.task.Task`)
        """
        return FakeDocuments()

if __name__ == "__main__":
    finestrino.run(['IndexDocuments', '--local-scheduler'])