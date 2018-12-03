import sys

import unittest

import finestrino
import finestrino.notifications

from finestrino.interface import _WorkerSchedulerFactory
from finestrino.worker import Worker 

from mock import Mock 

class InterfaceTest(unittest.TestCase):
    def setUp(self):
        self.worker = Worker()

        self.worker_scheduler_factory = _WorkerSchedulerFactory()
        self.worker_scheduler_factory.create_worker = Mock(return_value = self.worker)
        self.worker_scheduler_factory.create_local_worker = Mock()

        super(InterfaceTest, self).setUp()

        class NoOpTask(finestrino.Task):
            param = finestrino.Parameter()

        self.task_a = NoOpTask("a")
        self.task_b = NoOpTask("b")

    def test_interface_run_positive_path(self):
        self.worker.add = Mock(side_effect=[True, True])
        self.worker.run = Mock(return_value=True)

        self.assertTrue(self._run_interface())

    def _run_interface(self):
        return finestrino.interface.build([self.task_a, self.task_b], worker_scheduler_factory=self.worker_scheduler_factory)

