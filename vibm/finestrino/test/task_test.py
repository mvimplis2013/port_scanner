import doctest
import pickle 
import six
import warnings

from unittest import TestCase

from datetime import datetime, timedelta

import finestrino
import finestrino.task

class DummyTask(finestrino.Task):
    param = finestrino.Parameter()
    bool_param = finestrino.BoolParameter()
    int_param = finestrino.IntParameter()
    float_param = finestrino.FloatParameter()
    date_param = finestrino.DateParameter()
    datehour_param = finestrino.DateHourParameter()

class TaskTest(
    TestCase):
    def test_tasks_doctest(self):
        doctest.testmod(finestrino.task)

if __name__ == '__main__':
    unittest.main(TaskTest())

