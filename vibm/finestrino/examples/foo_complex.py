"""
You can run this example like this:

    ...code:: console

        $> rm -rf /tmp/bar
        $> finestrino --module examples.foo_complex examples.Foo --worker 2 --local-scheduler 
"""
from __future__ import division 
import time
import random

import finestrino

max_depth = 10
max_total_nodes = 50
current_nodes = 0

class Foo(finestrino.Task):
    task_namespace = 'examples'

    def run(self):
        print("Running Foo")

    def requires(self):
        global current_nodes

        for i in range( 30 // max_depth ):
            current_nodes += 1
            yield Bar(i)

class Bar(finestrino.Task):
    task_namespace = 'examples'

    num = finestrino.IntParameter()

    def run(self):
        time.sleep(1)

        self.output().open('w').close()

    def requires(self):
        global current_nodes

        if max_total_nodes > current_nodes:
            valor = int(random.uniform(1, 30))
            for i in range(valor // max_depth):
                current_nodes += 1
                yield Bar(current_nodes)

    def output(self):
        time.sleep(1)
        return finestrino.LocalTarget('/tmp/bar/%d' % self.num)

if __name__ == '__main__':
    Foo