from unittest import TestCase

import finestrino
import finestrino.scheduler
import finestrino.worker

from finestrino import notifications 

finestrino.notifications.DEBUG = True

class TaskStatusMessageTest(TestCase):
    def test_run(self):
        message = "test message"
        sch = finestrino.scheduler.Scheduler()

        with finestrino.worker.Worker(scheduler=sch) as w:
            class MyTask(finestrino.Task):
                def run(self):
                    self.set_status_message(message)

            task = MyTask()
            w.add(task)
            w.run()

            self.assertEqual(sch.get_task_status_message(task.task_id)["statusMessage"], message)

if __name__ == '__main__':
    unittest.main()