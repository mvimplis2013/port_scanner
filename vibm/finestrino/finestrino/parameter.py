'''Parameters are one of the core concepts of Finestrino.
All parameters sit on :class:`~finestrino.task.Task` classes.
'''
import abc 
import datetime
import warnings 
from enum import IntEnum
import json
from json import JSONEncoder
from collections import OrderedDict, Mapping
import operator
import functools
from ast import literal_eval

try:
    from configuration import NoOptionError, NoSectionError
except ImportError:
    from configparser import NoOptionError, NoSectionError

#from finestrino import task_register
from finestrino import six  
from finestrino import configuration
from finestrino.cmdline_parser import CmdlineParser 

_no_value = object()

class ParameterVisibility(IntEnum):
    PUBLIC = 0
    HIDDEN = 1
    PRIVATE = 2

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)

    def serialize(self):
        return self.value

class Parameter(object):
    '''Parameter whose value is a str and a base class for other parameter types.
    
    Parameters are objects set on the Task class level to make it possible to parameterize tasks.
    For instance:

    ... code:: python
        class MyTask(finestrino.Task):
            foo = finestrino.Parameter()

        class RequiringTask(finestrino.Task):
            def requires(self):
                return MyTask(foo="hello")

            def run(self):
                print(self.requires().foo)  # prints "hello"

    This makes it possible to instantiate multiple tasks, e.g. MyTask(foo='bar') and 
    MyTask(foo='baz'). The task will then have the foo attribute set appropriately.


    Arguments:
        object {[type]} -- [description]
    '''
    _counter = 0

    def __init__(self, default=_no_value, is_global=False, significant=True, description=None,
        config_path=None, positional=True, always_in_help=False, batch_method=None,
        visibility=ParameterVisibility.PUBLIC):
        
        self._default = default
        self._batch_method = batch_method

        if is_global:
            warnings.warn("is_global support is removed. Assuming positional=False",
                DeprecationWarning, stacklevel=2)
            positional = False

        self.significant = significant
        self.positional = positional
        self.visibility = visibility if ParameterVisibility.has_value(visibility) \
            else ParameterVisibility.PUBLIC

        self.description = description
        self.always_in_help = always_in_help

        if config_path is not None and ('section' not in config_path or 'name' not in config_path):
            raise ParameterException('config_path must be a hash containing entries for section and name')

        self._config_path = config_path

        self._counter = Parameter._counter
        Parameter._counter += 1

    def normalize(self, x):
        """Given a parsed parameter value, normalizes it.

        The value can either be the result of parse(), the default value
        or arguments passed into the task's constructor.
        
        Arguments:
            x {[type]} -- [description]
        """
        return x

    def _get_value_from_config(self, section, name):
        """Loads the default from the config. 
        Returns _no_value if it doesn't exist
        
        Arguments:
            section {[type]} -- [description]
            name {[type]} -- [description]
        """
        conf = configuration.get_config()

        try:
            value = conf.get(section, name)
        except (NoSectionError, NoOptionError, KeyError):
            return _no_value

        return self.parse(value)

    def _get_value(self, task_name, param_name):
        for value, warn in self._value_iterator(task_name, param_name):
            if value != _no_value:
                if warn:
                    warnings.warn(warn, DeprecationWarning)
                return value
            
        return no_value

    def _value_iterator(self, task_name, param_name):
        cp_parser = CmdlineParser.get_instance()
        if cp_parser:
            dest = self._parser_global_dest(param_name, task_name)
            found = getattr(cp_parser.known_args, dest, None)
            yield (self._parse_or_no_value(found), None)
        yield(self._get_value_from_config(task_name, param_name), None)
        yield(self._get_value_from_config(task_name, param_name.replace('_', '-')),
            'Configuration [{}] {} (with dashes) should be avoided. Please use underscores.'.format(
                task_name, param_name ))
        if self._config_path:
            yield(self._get_value_from_config(self._config_path['section'], 
                self._config_path['name']), 'The use of the configuration [{}] {} is deprecated. Please use [{}] {}'.format(
                    self._config_path['section'], self._config_path['name'], task_name, param_name))

        yield(self._default, None) 
    
    def task_value(self, task_name, param_name):
        value = self._get_value(task_name, param_name)

        if value == _no_value:
            raise MissingParameterException("No default specified")
        else:
            return self.normalize(value)

    def has_task_value(self, task_name, param_name):
        return self._get_value(task_name, param_name) != _no_value
        

class IntParameter(Parameter):
    def parse(self, s):
        return int(s)

    def next_in_enumeration(self, value):
        return value + 1

class FloatParameter(Parameter):
    '''Parameter whose value is a ``float``
    
    Arguments:
        Parameter {[type]} -- [description]
    '''

    def parse(self, s):
        '''Parses a float from the string using float()
        
        Arguments:
            s {[type]} -- [description]
        '''
        return float(s)

class BoolParameter(Parameter):
    IMPLICIT_PARSING = "implicit"
    EXPLICIT_PARSING = "explicit"

    parsing = IMPLICIT_PARSING

    def __init__(self, *args, **kwargs):
        self.parsing = kwargs.pop("parsing", self.__class__.parsing)
        super(BoolParameter, self).__init__(*args, **kwargs)
        if self._default == _no_value:
            self._default = False

    def parse(self, val):
        s = str(val).lower()
        if s == "true":
            return True
        elif s == "false":
            return False
        else:
            raise ValueError("cannot interpret '{}'".format(val)) 

class OptionalParameter(Parameter):
    """ A Parameter that treats empty string as None """
    def serialize(self, x):
        if x is None:
            return ''
        else:
            return str
        
    def parse(self, x):
        return x or None

    def _warn_on_wrong_parameter_type(self, param_name, param_value):
        if self.__class__ != OptionalParameter:
            return 
        if not instanceof(param_value, six.string_types) and param_value is not None:
            warnings.warn('OptionalParameter "{}" with value "{}" is not of type string '
            'or None.'.format(param_name, param_value)) 

_UNIX_EPOCH = datetime.datetime.utcfromtimestamp(0)

class _DateParameterBase(Parameter):
    """ Base class Parameter for date (not datetime) """
    def __init__(self, interval=1, start=None, **kwargs):
        super(_DateParameterBase, self).__init__(**kwargs)
        self.interval = interval
        self.start = start if start is not None else _UNIX_EPOCH.date()

class DateParameter(_DateParameterBase):
    """ Parameter whose value is a Date string formatted `YYYY-MM-DD`.

    DateParameters are 90% of the time used to be interpolated into file 
    system paths or the like
    """
    date_format = '%Y-%m-%d'
