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
    insignificant_param = finestrino.Parameter(significant=False)

DUMMY_TASK_OK_PARAMS = dict(
    param = 'test',
    bool_param = True,
    int_param = 666,
    float_param = 123.456,
    date_param = datetime(2014, 9, 13).date(),
    datehour_parameter = datetime(2014, 9, 13, 9),
    timedelta_parameter = timedelta(44),   # Doesn't support seconds
    insignificant_param = 'test'
)

class DefaultInsignificantParamTask(finestrino.Task):
    insignificant_param = finestrino.Parameter(significant=False, default='value')
    necessary_param = finestrino.Parameter(significant=False)

class TaskTest(unittest.TestCase):
    def test_tasks_doctest(self):
        doctest.testmod(finestrino.task)

    def test_task_to_str_to_task(self):
        original = DummyTask(**DUMMY_TASK_OK_PARAMS)
        other = DummyTask.from_str_params(original.to_str_params())
        self.assertEqual(original, other)

    def test_task_from_str_insignificant(self):
        params = {'necessary_parma': 'needed'}
        original = DefaultInsignificantParamTask(**params)
        other = DefaultInsignificantParamTask.test_task_from_str_params(params)
        assertEqual(original, other)

    def test_task_missing_necessary_param(self):
        with self.assertRaises(finestrino.parameter.MissingParameterException):
            DefaultInsignificantParamTask.from_str_params({})

if __name__ == '__main__':
    unittest.main(TaskTest())

