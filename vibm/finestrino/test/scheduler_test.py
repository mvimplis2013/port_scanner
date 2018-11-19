from __future__ import print_function

import pickle
import tempfile
import time
import unittest

import finestrino.scheduler
from helpers import with_config 

class SchedulerIoTest(unittest.TestCase):
    def setUp(self):
        self.scheduler = finestrino.scheduler.Scheduler()

    def test_pretty_id_unicode(self):
        self.scheduler.add_task(worker='A', task_id = '1', 
            params={u'foo': u'\u2192bar'})
        [task] = list(scheduler._state.get_active_tasks())
        task.pretty_id

    def test_load_old_state(self):
        tasks = {}
        active_workers = {'Worker1': 1e9, 'Worker2': time.time()}

        with tempfile.NamedTemporaryFile(delete=True) as fn:
            with open(fn.name, 'wb') as fobj:
                state = (tasks, active_workers)
                pickle.dump(state, fobj)

            state = finestrino.scheduler.SimpleTaskState(
                state_path = fn.name
            )
            
            state.load()

            self.assertEqual(set(state.get_worker_ids()), {'Worker1', 'Worker2'})

    def test_load_broken_state(self):
        with tempfile.NamedTemporaryFile(delete=True) as fn:
            with open(fn.name, 'w') as fobj:
                print("b0rk", file=fobj)

            state = finestrino.scheduler.SimpleTaskState(
                state_path = fn.name
            )

            state.load()

            self.assertEqual(list(state.get_worker_ids()), [])

    @with_config({'scheduler': {'retry_count': '44', 'worker_disconnect_delay': '55'}})
    def test_scheduler_with_config(self):
        scheduler = finestrino.scheduler.Scheduler()
        self.assertEqual(44, scheduler._config.retry_count)
        self.assertEqual(55, scheduler._config.worker_disconnect_delay)

        # Override 
        scheduler = finestrino.scheduler.Scheduler(retry_count=66,
            worker_disconnect_delay=77)
        self.assertEqual(66, scheduler._config.retry_count)
        self.assertEqual(77, scheduler._config.worker_disconnect_delay)

    @with_config({'resources': {'a': '100', 'b': '200'}})
    def test_scheduler_with_resources(self):
        scheduler = finestrino.scheduler.Scheduler()
        self.assertEqual({'a': 100, 'b': 200}, scheduler._resources)

    @with_config({'scheduler': {'record_task_history': 'True'},
        'task_history': {'db_connection': 'sqliet:////none/existing/path/list.db'}})
    def test_local_scheduler_task_history_status(self):
        ls = finestrino.interface._WorkerSchedulerFactory.create_local_scheduler()
        self.assertEqual(False, ls._config.record_task_history)