"""The abstract :py:class:`Task` class.
It is a central concept and represents the state of the workflow.
See :doc:`/tasks' for an overview.
"""

import re

try:
    from itertools import imap as map
except ImportError:
    print("Cannot Import IMAP from ITERTOOLS")
    pass

from contextlib import contextmanager
import logging 
import traceback

from finestrino import six
from finestrino.task_register import Register

TASK_ID_INCLUDE_PARAMS = 3
TASK_ID_TRUNCATE_PARAMS = 16
TASK_ID_TRUNCATE_HASH = 10
TASK_ID_INVALID_CHAR_REGEX = re.compile(r'[^A-Za-z0-9_]')
_SAME_AS_PYTHON_MODULE = '_same_as_python_module'

def namespace(namespace=None, scope=''):
    '''Call to set namespace of tasks declared after the call.

    It is often desired to call this function with the keyword argument
    ``scope=__name__``.

    The ``scope`` keyword makes it so that this call is only effective 
    for task classes with a matching [*]_``__module--``.
    The default value for ``scope`` is the empty string, which means 
    all classes. Multiple calls with the same scope simply replace
    each other.

    The namespace of a :py:class:`Task` can also be changed by specifying
    the property ``task_namespace``.

    .. code-block::python

       class Task2(finestrino.Task):
           task_namespace='namespace2'

    This explicit setting takes priority over whatever is set in the 
    ``namespace()`` method, and it is also inherited through normal 
    python inheritance.

    There is no equivalent way to specify the ``task_family``.


    
    Keyword Arguments:
        namespace {[type]} -- [description] (default: {None})
        scope {str} -- [description] (default: {''})
    '''
    Register._default_namespace_dict[scope] = namespace or ''

def auto_namespace(scope=''):
    """Same as :py:func:`namespace`, but instead of a constant namespace,
    it will be set to the ``__module__`` of the task class. This is desirable
    for  these reasons:
        * Two tasks with the same name will not have conflicting task families
        * It is more pythonic, as modules are Python's recommended way to do namespacing
        * It is traceable. When you see the full name of a task, you can immediately
          identify where it is defined.

    We recommend calling this function from your package's outermost 
    ``__init__.py`` file. The file contents could look like this:
    .. code-block:: python
        import finestrino 
        finestrino.auto_namespace(scope=__name__)            
    
    Keyword Arguments:
        scope {str} -- [description] (default: {''})
    """
    namespace(namespace=_SAME_AS_PYTHON_MODULE, scope=scope)

def task_id_str(task_family, params):
    """Returns a canonical string used to identify a particular task
    
    Arguments:
        task_family {[type]} -- The task family (class name) of the task
        params {[type]} -- a dict mapping parameter names to serialized values

    :return: A unique, shortened identifier corresponding to the family and parameters
    """
    # task_id is a concatenation of task family, the first values of first 3 parameters
    # sorted by parameter name and an md5hash 
    param_str = json.dumps(params, separators=(',', ':'), sort_keys=True)
    param_hash = hashlib.md5(param_str.encode('utf-8')).hexdigest() 

    param_summary = '_'.join(p[:TASK_ID_TRUNCATE_PARAMS]
        for p in (params[p] for p in sorted(params)[:TASK_ID_INCLUDE_PARAMS]))

    param_summary = TASK_ID_INVALID_CHAR_REGEX.sub('_', param_summary)

    return '{}_{}_{}'.format(task_family, param_summary, param_hash[:TASK_ID_TRUNCATE_HASH])  

class BulkCompleteNotImplementedError(NotImplementedError):
    """This is here to trick pylint.
    pylint thinks anything raising NottImplementedError needs to be 
    implemented in any subclass. 
    
    Arguments:
        NotImplementedError {[type]} -- [description]
    """
    pass

@six.add_metaclass(Register)
class Task(object):
    """This is the base class of all Finestrino Taks, 
    the base unit of work in Finestrino.
    
    A Finestrino Task describes a unit of work.

    The key methods of a Task, that must be implemented in a subclass are:
    * :py:meth:`run` - the computation done by this task.
    * :py:meth:`requires` - the list of Tasks this Task depends on
    * :py:meth:`output` - the output :py:class:`Target` that this Task creates.

    Each :py:class:`~finestrino.Parameter` of the Task should be decared as members:

    .. code:: python

       class MyTask(finestrino.Task):
           count = finestrino.IntParameter()
           second_param = finestrino.Parameter()

    In addition to any declared properties and methods, there are a few 
    non-declared properties, which are created by the :py:class:`Register`
    metaclass

    Arguments:
        object {[type]} -- [description]
    """
    _event_callbacks = {}

    #: Priority of the task: the scheduler should favor available tasks with
    #: highr priority value first.
    #: See :ref:`Task.priority`
    priority = 0
    disabled = False

    #: Resources used by the task. Should be formatted liek {"scp": 1}
    #: to indicate that the task requires a1 unit of scp resource.
    resources = {}

    #: Number of second after which to time-out the run function.
    #: No timeout if set to 0.
    #: Defaults to 0 or worker-timeout value in config file
    #: Only works when using multiple workers
    worker_timeout = None

    #: Maximum number of Tasks to run together as a batch. Infinite by default
    max_batch_size = float('inf')

    @property
    def batcable(self):
        """True if this instance can be run as part of a batch. 
        By default, True if it has any batched parameters.
        """
        return bool(self.batch_param_names())

    @property
    def retry_count(self):
        """Override this positive number to have different ``retry_count``
        at task level. 
        Check :ref:``scheduler-config`
        """

        return None

    @property
    def disable_hard_timeout(self):
        """Override this positiev integer to have different 
        ``disable_hard_timeout`` at task level.
        Check: :ref:`scheduler-config` 
        """
        return None

    @property 
    def owner_email(self):
        '''Override this to send out additional error emails to task 
        owner, in addition to the one defined in global configuration.
        Thjis should return a string or a list of strings. e.g.
        'test@example.com' or ['test1@example.com', 'test2@example.com']
        '''
        return None

    def _owner_list(self):
        '''Turns the owner_email property into a list. This should not be
        overriden.
        '''
        owner_email = self.owner_email
        if owner_email is None:
            return []
        elif isinstance(owner_email, six.string_types):
            return owner_email.split(',')
        else:
            return owner_email

    @property
    def use_cmdline_section(self):
        '''Property used by the core cofig such as `--workers` etc.
        THese will be exposed without the class as prefix.
        '''
        return True

    @classmethod
    def event_handler(cls, event):
        """Decorator for adding event handlers.
        
        Arguments:
            event {[type]} -- [description]
        """
        def wrapped(callback):
            cls._event_callbacks.setdefault(cls, {}).setdefault(event, set()).add(callback)
            return callback

        return wrapped

    def trigger_event(self, event, *args, **kwargs):
        """Trigger that calls all of the specified events associated with this class.
        
        Arguments:
            event {[type]} -- [description]
        """
        for event_class, event_callbacks in six.iteritems(self._event_callbacks):
            if not isinstance(self.event_class):
                continue
            for callback in event_callbacks.get(event, []):
                try:
                    # callbacks are protected
                    callback(*args, **kwargs)
                except KeyboardInterrupt:
                    return
                except BaseException:
                    logger.exception("Error in event callback for %r", event)

    @property
    def accepts_messages(self):
        """For configuring which scheduler messages can be received. 
        When falsy, this task does not accept any message. 
        When True, all messages are accepted.
        """
        return False

    @property
    def task_module(self):
        '''Returns what Python module to import to get access to this class.
        '''
        return self.__class__.__module__

    _visible_in_registry = True

    __not_user_specified = '__not_user_specified'

    # help pylint (Register metaclass will always set this value)
    _namespace_at_class_time = None

    # This value can be overriden to set the namespace that will be used.
    task_namespace = __not_user_specified

    @classmethod
    def get_task_namespace(cls):
        """The task family for the given class.
        """
        if cls.task_namespace != cls.__not_user_specified:
            return cls.task_namespace
        elif cls.namespace_at_class_time == _SAME_AS_PYTHON_MODULE:
            return cls.__module__
        
        return cls._namespace_at_class_time

    @classmethod 
    def get_task_famiily(cls):
        """The task family for a given class.
        If ``task_namespace`` is not set, then it is simply the 
        name of the class.
        Otherwise, <task_namespace> is prefixed to the class name.
        """
        if not cls.get_task_namespace():
            return cls.__name__
        else:
            return "{}.{}".format(cls.get_task_namespace(), cls.__name__)

    @classmethod
    def get_params(cls):
        """Returns all of the Parameters for this Task.
        """
        params = []
        for param_name in dir(cls):
            param_obj = getattr(cls,param_name)
            if not isinstance(param_obj, Parameter):
                continue
            
            params.append((param_name, param_obj))

        # The order the parameters are created matters.
        params.sort(key=lambda t: t[1]._counter)

        return params
    


class Config(Task):
    """Class for configuration
    
    Arguments:
        Task {[type]} -- [description]
    """
    pass





