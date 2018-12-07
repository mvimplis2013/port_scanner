"""The abstract :py:class:`Task` class.
It is a central concept and represents the state of the workflow.
See :doc:`/tasks' for an overview.
"""
import json 
import hashlib

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

from finestrino import parameter
from finestrino.parameter import ParameterVisibility

Parameter = parameter.Parameter
logger = logging.getLogger('finestrino-interface')

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

def flatten(struct):
    """
    Creates a flat list of all the items in structured output (dicts, lists, items):

    .. code-block:: python
        >>> sorted(flatten(['foo', ['bar', 'troll']))
        ['bar', 'foo', 'troll']
    """
    if struct is None:
        return []
    
    flat = []

    if isinstance(struct, dict):
        for _, result in six.iteritems(struct):
            flat += flatten(result)
        
        return flat

    if isinstance(struct, six.string_types):
        return [struct]

    try:
        iterator = iter(struct)
    except TypeError:
        return [struct]

    for result in iterator:
        flat += flatten(result)

    return flat

def flatten_output(task):
    r = flatten(task.output())
    if not r:
        for dep in flatten(task.requires()):
            r += flatten_output(dep)

    return r

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
    def batchable(self):
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
    def disable_window_seconds(self):
        """ 
        Override this positive integer to have different ``disable_window_seconds``
        at task level.
        Check :ref:scheduler-config`
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
        elif cls._namespace_at_class_time == _SAME_AS_PYTHON_MODULE:
            return cls.__module__
        
        return cls._namespace_at_class_time

    @property
    def task_family(self):
        """ 
        DEPRECATED since after 2.4.0. See :py:meth:`get_task_family` instead.
        
        Convenience method since a property on the metaclass isn't directly 
        accessible through the class instances.
        """
        return self.__class__.task_family

    @classmethod
    def get_task_family(cls):
        """The task family for the given class.
        
        If ``task_namespace`` is not set, then it is simply the name of the class. 
        Otherwise ``<task_namespace>.`` is prefixed to the class name.
        
        Returns:
            [type] -- [description]
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

    @classmethod
    def get_param_values(cls, params, args, kwargs):
        result = {}

        params_dict = dict(params)

        task_family = cls.get_task_family

        # In case any exceptions are thrown
        exc_desc = '%s[args=%s, kwargs=%s]' % (task_family, args, kwargs)

        # Fill in the positional arguments
        positional_params = [(n,p) for n, p in params if p.positional]

        for i, arg in enumerate(args):
            if i >= len(positional_params):
                raise parameter.UnknownParameterException('%s: takes at most %d parameters (%d given)' % (exc_desc, len(positional_params), len(args)))
        
            param_name, param_obj = positional_params[i]
            result[param_name] = param_obj.normalize(arg)

        # Then the keyword arguments
        for param_name, arg in six.iteritems(kwargs):
            if param_name in result:
                raise parameter.DuplicateParameterException('%s: parameter %s was already set a positional parameter' % (exc_desc, param_name))
            if param_name not in params_dict:
                raise parameter.UnknownParameterException(
                    '%s: unknown parameter %s' % (exc_desc, param_name))
            result[param_name] = params_dict[param_name].normalize(arg)

        # Then use the defaults for anything not filled in
        for param_name, param_obj in params:
            if param_name not in result:
                if not param_obj.has_task_value(task_family, param_name):
                    raise parameter.MissingParameterException("%s: requires the '%s' parameter to be set" % (exc_desc, param_name))
                result[param_name] = param_obj.task_value(task_family, param_name)

        def list_to_tuple(x):
            if isinstance(x, list) or isinstance(x, set):
                return tuple(x)
            else:
                return x

        # Sort it by the correct order and make a list
        return [(param_name, list_to_tuple(result[param_name])) for param_name, param_obj in params]
    
    def __init__(self, *args, **kwargs):
        params = self.get_params()
        param_values = self.get_param_values(params, args, kwargs)

        # Set all values
        for key, value in param_values:
            setattr(self, key, value)

        # Register kwargs as an attribute on the class 
        self.param_kwargs = dict(param_values)

        self._warn_on_wrong_param_types()
        self.task_id = task_id_str(self.get_task_family(), self.to_str_params(only_significant=True, only_public=True))
        self.__hash = hash(self.task_id)

        self.set_tracking_url = None
        self.set_status_message = None
        self.set_progress_percentage = None

    @classmethod
    def from_str_params(cls, params_str):
        """Creates an instance from a str->str hash.
        
        Arguments:
            params_str {[type]} -- dict of param name
        """
        kwargs = {}
        for param_name, param in cls.get_params():
            if param_name in params_str:
                param_str = params_str[param_name]
                if isinstance(param_str, list):
                    kwargs[param_name] = param._parse_list(param_str)
                else:
                    kwargs[param_name] = param.parse(param_str)

        return cls(**kwargs)

    def to_str_params(self, only_significant=False, only_public=False):
        """Convert all parameters to a str->str hash
        
        Keyword Arguments:
            only_significant {bool} -- [description] (default: {False})
            only_public {bool} -- [description] (default: {False})
        """
        params_str = {}
        params = dict(self.get_params())
        for param_name, param_value in six.iteritems(self.param_kwargs):
            if (((not only_significant) or params[param_name].significant) 
                and ((not only_public) or params[param_name].visibility == ParameterVisibility.PUBLIC)
                and params[param_name].visibility != ParameterVisibility.PRIVATE):
                params_str[param_name] = params[param_name].serialize(param_value)

        return params_str

    def _warn_on_wrong_param_types(self):
        params = dict(self.get_params())
        for param_name, param_value in six.iteritems(self.param_kwargs):
            params[param_name]._warn_on_wrong_param_type(param_name, param_value)

    def initialized(self):
        """ 
        Returns `True` if the  Task is initialized or False otherwise.
        """

        return hasattr(self, 'task_id') 

    def deps(self):
        """ 
        Internal method used by the scheduler.

        Returns the flattened list of requires.
        """
        return flatten(self._requires()) 

    def requires(self):
        """ 
        The Tasks that this Task depends on. 

        A Task will only run if all the Tasks that it requires are completed.
        If your Task does not require any other Tasks, then you don't need to
        override this method. Otherwise, a subclass can override this method
        to return a single Task, a list of Task instances, or a dictionary 
        whose values are Task instances.
        """ 
        return [] #default implementation

    def _requires(self):
        """ 
        Override in "template" tasks which themselves are supposed to be 
        subclassed and thus have their requires() overriden.

        Must return an iterable which among others contains the _requires()
        of the superclass.
        """
        return flatten(self.requires()) # base impl

    def process_resources(self):
        """ 
        Override in "template" tasks which provide common resources functionality
        but allow subclasses to specify additional resources while preserving
        the name for consistent end-user experience.
        """
        return self.resources # default implementation      

    @classmethod
    def batch_param_names(cls):
        return [name for name, p in cls.get_params() if \
            include_significant or p.significant]

class Config(Task):
    """Class for configuration
    
    Arguments:
        Task {[type]} -- [description]
    """
    pass

class ExternalTask(Task):
    """ Subclass for references to external dependencies.

    An ExternalTask's does not have a `run` implementation, which signifies to
    the framework that this Task's :py:meth:`output` is generated outside of
    finestrino.
    """
    run = None




