import abc
import logging

from finestrino import six

logger = logging.getLogger('finestrino-interface')

class StoredTask(object):
    """
    Interface for methods on TaskHistory
    """

    # TODO : do we need this task as distinct from luigi.scheduler.Task?
    #        this only records host and record_id in addition to task parameters.

    def __init__(self, task, status, host=None):
        self._task = task
        self.status = status
        self.record_id = None
        self.host = host

    @property
    def task_family(self):
        return self._task.family

    @property
    def parameters(self):
        return self._task.params

@six.add_metaclass(abc.ABCMeta)
class TaskHistory(object):
    @abc.abstractmethod
    def task_scheduled(self, task):
        pass

    @abc.abstractmethod
    def task_finished(self, task, successful):
        pass

    @abc.abstractmethod
    def task_started(self, task, worker_host):
        pass

    # TODO(mvimplis): should web method (find_latest_runs etc)

class NopHistory(TaskHistory):
    def task_scheduled(self, task):
        pass

    def task_finished(self, task, successful):
        pass

    def task_started(self, task, worker_host):
        pass
