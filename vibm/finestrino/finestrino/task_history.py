import abc
import logging

from finestrino import six

logger = logging.getLogger('finestrino-interface')

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
