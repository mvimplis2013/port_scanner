from unittest import TestCase

import finestrino 

from finestrino.worker import TaskException

class WorkerTaskTest(TestCase):
    def test_constructor(self):
        class MyTask(finestrino.Task):
            def __init__(self):
                pass

        def f():
            finestrino.build([MyTask()], local_scheduler=True)

        self.assertRaises(TaskException, f)

