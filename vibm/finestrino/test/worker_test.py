import time

import unittest

import finestrino.notifications

from finestrino.scheduler import Scheduler
from finestrino.worker import Worker

finestrino.notifications.DEBUG = True

class WorkerTest(unittest.TestCase):
    def run(self, result=None):
        self.sch = Scheduler(retry_delay=100, remove_delay=1000, worker_disconnect_delay=10)
        
        self.time = time.time

        with Worker(scheduler=self.sch, worker_id='X') as w, 
                Worker(scheduler=self.sch, worker_id='Y') as w2:
            self.w = w
            self.w2 = w2
            super(WorkerTest, self).run(result)

        if time.time != self.time:
            time.time = self.time

    def setTime(self, t):
        time.time = lambda: t
    
    def test_dep(self):
        class A(Task):
            def run(self):
                self.has_run = True
            
            def complete(self):
                return self.has_run

        a = A()

        class B(Task):
            def requires(self):
                return a

            def run(self):
                self.has_run = True

            def complete(self):
                return self.has_run

        b = B()
        a.has_run = False
        b.has_run = False

        self.assertTrue(self.w.add(b))
        self.assertTrue(self.w.run())
        self.assertTrue(a.has_run)
        self.assertTrue(b.has_run)

if __name__ == "__main__":
    unittest.main()