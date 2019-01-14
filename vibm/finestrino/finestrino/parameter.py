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
    from ConfigParser import NoOptionError, NoSectionError
except ImportError:
    from configparser import NoOptionError, NoSectionError

#from finestrino import task_register
from finestrino import six  
from finestrino import configuration
from finestrino.cmdline_parser import CmdlineParser 

_no_value = object()

class ParameterException(Exception):
    """Base Exception
    
    Arguments:
        Exception {[type]} -- [description]
    """
    pass

class DuplicateParameterException(ParameterException):
    """
    Exception signifying that a Parameter was specified multiple times.
    """
    pass

class UnknownParameterException(ParameterException):
    """Exception signifying that an unknown Parameter was supplied.
    
    Arguments:
        ParameterException {[type]} -- [description]
    """
    pass

class MissingParameterException(ParameterException):
    """Exception signifying that there was a missing parameter.
    
    Arguments:
        ParameterException {[type]} -- [description]
    """
    pass

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

    def parse(self, x):
        """Parse an individual value from the input.

        The default implementation is the identity function, but subclasses should override this method for specialized parsing.
        
        Arguments:
            x {[type]} -- [description]
        """
        return x # default impl

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
            
        return _no_value

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

    def _is_batchable(self):
        return self._batch_method is not None

    def _parse_list(self, xs):
        """ 
        Parse a list of values from the scheduler.

        Only possible if this is_batchable() is True. This function will combine the list into a single 
        parameter value using batch method.

        :param xs: list of values to parse and combine
        :return: the combined parsed values
        """
        if not self._is_batchable():
            raise NotImplementedError('No batch method found!')
        elif not xs:
            raise ValueError('Empty parameter list passed to parse_list()')
        else:
            return self._batch_method(map(self.parse, xs))
    
    def serialize(self, x):
        """
        Opposite of :py:meth:`parse`.

        :param x: the value to serialize.
        """
        return str(x)

    def _warn_on_wrong_param_type(self, param_name, param_value):
        if self.__class__ != Parameter:
            return
        if not isinstance(param_value, six.string_types):
            warnings.warn('Parameter "{}" with value "{}" is not of type string.'.format(param_name, param_value))

    def normalize(self, x):
        """Given a parsed parameter value, normalizes it.

        The value can either be the result of parse(), the default value
        or arguments passed into the task's constructor.
        
        Arguments:
            x {[type]} -- [description]
        """
        return x

    def next_in_enumeration(self, _value):
        """ 
        If your Parameter type has an enumerable ordering of values. You can 
        choose to override this method. This method is used by the 
        :py:meth:`finestrino.execution_summary` module for pretty printing purposes.
        Enabling it to pretty print tasks like ``MyTask(num=1), MyTask(num=2), MyTask(num=3)`` to ``MyTask(num=1..3)``.

        :param value: The value 
        :return: The next value, like "value+1" OR ``None`` if there is no enumerable ordering.
        """
        return None

    def _parse_or_no_value(self, x):
        if not x:
            return _no_value
        else:
            return self.parse(x)

    @staticmethod
    def _parser_global_dest(param_name, task_name):
        return task_name + '_' + param_name

    @classmethod
    def _parser_kwargs(cls, param_name, task_name=None):
        return {
            "action": "store",
            "dest": cls._parser_global_dest(param_name, task_name) if task_name else param_name,
        }

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

    def normalize(self, value):
        try: 
            return self.parse(value)
        except ValueError:
            return None

    def _parser_kwargs(self, *args, **kwargs):
        parser_kwargs = super(BoolParameter, self)._parser_kwargs(*args, **kwargs)

        if self.parsing == self.IMPLICIT_PARSING:
            parser_kwargs["action"] = "store_true"
        elif self.parsing == self.EXPLICIT_PARSING:
            parser_kwargs["nargs"] = "?"
            parser_kwargs["const"] = True
        else:
            raise ValueError("unknown parsing value '{}'".format(self.parsing))

        return parser_kwargs

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

    @abc.abstractproperty
    def date_format(self):
        """Override me with a :py:meth:`~datetime.date.strftime` string
        """
        pass

    def parse(self, s):
        """Parses a date string formatted like ```YYY-MM-DD``.
        
        Arguments:
            s {[type]} -- [description]
        """
        return datetime.datetime.strptime(s, self.date_format).date()

    def serialize(self, dt):
        """Converts the date to a string using the :py:attr:`~_DateParameterBase.date_format`
        
        Arguments:
            dt {[type]} -- [description]
        """
        if dt is None:
            return str(dt)

        return dt.strftime(self.date_format)

class DateParameter(_DateParameterBase):
    """ Paramter whose value is a :py:class:`datetime.date`.
    A DateParameter is a Date string formatted ``YYYY-MM-DD``. For example,
    `2013-07-10`` specifies July 10, 2013.
    
    DateParameters are 90% of the time used to be interpolated into file 
    system paths or the like.

    .. code:: python
         class MyTask(finestrino.Task):
             date = finestrino.DateParameter()

             def run(self):
                 templated_path = "/my/path/to/my/dataset{date:%Y/%m/%d}/"
                 instantiated_path = templated_path.format(date=self.date)
    """
    date_format = '%Y-%m-%d'

    def next_in_enumeration(self, value):
        return value + datetime.timedelta(days=self.interval)

    def normalize(self, value):
        if value is None:
            return None

        if isinstance(value, datetime.datetime):
            value = value.date()

        delta = (value - self.start).days % self.interval

        return value - datetime.timedelta(days=delta)

class _DatetimeParameterBase(Parameter):
    """Base class Parameter for datetime
    
    Arguments:
        Parameter {[type]} -- [description]
    """
    def __init__(self, interval=1, start=None, **kwargs):
        super(_DatetimeParameterBase, self).__init__(**kwargs)
        self.interval = interval
        self.start = start if start is not None else _UNIX_EPOCH

    @abc.abstractproperty
    def _timedelta(self):
        """How to move one interval of this type forward (i.e. not counting self.interval)
        """
        pass

    def parse(self, s):
        """Parses a string to a :py:class:`~datetime.datetime`
        
        Arguments:
            s {[type]} -- [description]
        """
        return datetime.datetime.strptime(s, self.date_format)

    def serialize(self,dt):
        """Converts the date to a string using the :py:attr:`~_DatetimeParameterBase.date_format`.
        
        Arguments:
            dt {[type]} -- [description]
        """
        if dt is None:
            return str(dt)

        return dt.strftime(self.date_format)
    

class DateHourParameter(_DatetimeParameterBase):
    """Parameter whose value is a :py:class:`~datetime.datetime` specified to the hour.

    A DateHourParameter is a ``2013-07-10T19`` specifies a ``July 10, 2013 at 19:00``.
    
    Arguments:
        _DatetimeParameterBase {[type]} -- [description]
    """
    date_format = '%Y-%m-%dT%H' # iso 8601 is to use 'T'
    _timedelta = datetime.timedelta(hours=1)

class TimeDeltaParameter(Parameter):
    """Class that maps to timedelta using strings in any of the following forms:

    ``n {w[eek[s]]|d[ay[s]]|h[our[s]]|m[inute[s]]|s[econd[s]]}`` (e.g. ``1 week 2 days`` or ``1 h``)
    
    Arguments:
        Parameter {[type]} -- [description]
    """
    def _apply_regex(self, regex, input):
        import re
        re_match = re.match(regex, input)
        if re_match and any(re_match.groups()):
            kwargs = {}
            has_val = False
            for k, v in six.iteritems(re_match.groupdict(default="0")):
                val = int(v)
                if val > -1:
                    has_val = True
                    kwargs[k] = val
                if has_val:
                    return datetime.timedelta(**kwargs)

class ChoiceParameter(Parameter):
    """ 
    A Parameter which takes two values:
        1. an instance of :class:`~collections.Iterable` and 
        2. the class of the variables to convert to

    In the Task definition, use:
    .. code-block:: python
        class MyTask(finestrino.Task):
            my_param = finestrino.ChoiceParameter(choices=[0.1, 0.2, 0.3], var_type = float)

    At the command line, use:
    .. code-block:: console
        $finestrino --module my_tasks MyTask --my-param 0.1

    Consider using :class:`~finestrino.EnumParameter` for a typed, structured
    alternative. This class can perform the same role when all choices are 
    the same type and transparency of parameter value on the command line is 
    desired.
    """     
    
    def __init__(self, var_type=str, *args, **kwargs):
        """ 
        :param function var_type: The type of the input variable, e.g. str, 
            int, float, etc.
        :param choises: An iterable, all of whose elements are of `var_type`
            to restrict parameter choices to.
        """ 
        if "choices" not in kwargs:
            raise ParameterException("A choices iterable must be specified")

        self._choices = set( kwargs.pop("choices") )
        self._var_type = var_type

        assert all(type(choice) is self._var_type for choice in self._choices), "Invalid type in choices"

        super(ChoiceParameter, self).__init__(*args, **kwargs)

        if self.description:
            self.description += " "
        else:
            self.description = ""

        self.description += (
            "Choices: {" + ", ".join(str(choice) for choice in self._choices) + "}"
        )

    def parse(self, s):
        var = self._var_type(s)
        return self.normalize(var)

    def normalize(self, var):
        if var in self._choices:
            return var
        else:
            raise ValueError("{var} is not a valid choice from {choices}".format(
                var = var, choices = self._choices                
            ))  

class EnumParameter(Parameter):
    """
    A parameter whose value is an :class:`~enum.Enum`.

    In the task definition, use

    .. code-block:: python

        class Model(enum.Enum):
          Honda = 1
          Volvo = 2

        class MyTask(luigi.Task):
          my_param = luigi.EnumParameter(enum=Model)

    At the command line, use,

    .. code-block:: console

        $ luigi --module my_tasks MyTask --my-param Honda

    """

    def __init__(self, *args, **kwargs):
        if 'enum' not in kwargs:
            raise ParameterException('An enum class must be specified.')
        self._enum = kwargs.pop('enum')
        super(EnumParameter, self).__init__(*args, **kwargs)

    def parse(self, s):
        try:
            return self._enum[s]
        except KeyError:
            raise ValueError('Invalid enum value - could not be parsed')

    def serialize(self, e):
        return e.name

class ListParameter(Parameter):
    """
    Parameter whose value is a ``list``.

    In the task definition, use

    .. code-block:: python

        class MyTask(luigi.Task):
          grades = luigi.ListParameter()

            def run(self):
                sum = 0
                for element in self.grades:
                    sum += element
                avg = sum / len(self.grades)


    At the command line, use

    .. code-block:: console

        $ luigi --module my_tasks MyTask --grades <JSON string>

    Simple example with two grades:

    .. code-block:: console

        $ luigi --module my_tasks MyTask --grades '[100,70]'
    """

    def normalize(self, x):
        """
        Ensure that struct is recursively converted to a tuple so it can be hashed.

        :param str x: the value to parse.
        :return: the normalized (hashable/immutable) value.
        """
        return _recursively_freeze(x)

    def parse(self, x):
        """
        Parse an individual value from the input.

        :param str x: the value to parse.
        :return: the parsed value.
        """
        return list(json.loads(x, object_pairs_hook=_FrozenOrderedDict))

    def serialize(self, x):
        """
        Opposite of :py:meth:`parse`.

        Converts the value ``x`` to a string.

        :param x: the value to serialize.
        """
        return json.dumps(x, cls=_DictParamEncoder)

class DateIntervalParameter(Parameter):
    """
    A Parameter whose value is a :py:class:`~luigi.date_interval.DateInterval`.

    Date Intervals are specified using the ISO 8601 date notation for dates
    (eg. "2015-11-04"), months (eg. "2015-05"), years (eg. "2015"), or weeks
    (eg. "2015-W35"). In addition, it also supports arbitrary date intervals
    provided as two dates separated with a dash (eg. "2015-11-04-2015-12-04").
    """

    def parse(self, s):
        """
        Parses a :py:class:`~luigi.date_interval.DateInterval` from the input.

        see :py:mod:`luigi.date_interval`
          for details on the parsing of DateIntervals.
        """
        # TODO: can we use xml.utils.iso8601 or something similar?

        from finestrino import date_interval as d

        for cls in [d.Year, d.Month, d.Week, d.Date, d.Custom]:
            i = cls.parse(s)
            if i:
                return i

        raise ValueError('Invalid date interval - could not be parsed')



