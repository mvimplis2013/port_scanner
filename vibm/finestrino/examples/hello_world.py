"""
You can run this example like this:

.. code:: console
    $luigi --module examples.hello_world examples.HelloWorldTask --local-scheduler

If that does not work, see :ref:`CommandLine`.
"""

import finestrino

class HelloWorldTask(finestrino.Task):
    task_namespace = 'examples'

    def run(self):
        print("{task} says: Hello world!".format(task=self.__class__.__name__))

if __name__ == '__main__':
    finestrino.run(['examples.HelloWorldTask', '--local-scheduler'])