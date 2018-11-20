"""Define the centralized register of all :class:`finestrino.task.Task` classes  
"""

import abc
import logging 

from finestrino import six

logger = logging.getLogger('finestrino-interface')

class TaskClassException(Exception):
    pass

class TaskClassNotFoundException(TaskClassException):
    pass

class TaskClassAmbigiousException(TaskClassException):
    pass

class Register(abc.ABCMeta):
    """The Metaclass of :py:class:`Task`

    Acts as a global registry of Tasks with the following properties:

    1) Cache instances of objects so that e.g. ``X(1, 2, 3)`` always 
       returns the same object.
    2) Keep track of all subclasses of :py:class:`Task` and expose them.
    
    Arguments:
        abc {[type]} -- [description]
    """
    __instance_cache = {}
    _default_namespace_dict = {}
    _reg = []

    AMBIGUOUS_CLASS = object() # Placeholder denoting an error
    """If this value is returned by :py:meth:`_get_reg` then there is an
    ambiguous task name (two :py:class:`Task` have the same name). 
    This denotes an error.
    """
    def __new__(metacls, classname, bases, classdict):
        """Custom class creation for namespacing.

        Also register all subclasses.

        When the set or inherited namespaces evaluates to `None`, set the 
        tak namespace to whatever the currently declared namespace is. 
        
        Arguments:
            metacls {[type]} -- [description]
            classname {[type]} -- [description]
            bases {[type]} -- [description]
            classdict {[type]} -- [description]
        """
        cls = super(Register, metacls).__new__(metacls, classname, bases, classdict)
        cls._namespace_at_class_time = metacls._get_namespace(cls.__module__)
        metacls._reg.append(cls)

        return cls

    @staticmethod
    def _module_parents(module_name):
        '''
        >>> list(Register._module_parents('a.b))
        ['a.b', 'a', '']
        
        Arguments:
            module_name {[type]} -- [description]
        '''
        spl = module_name.split('.')
        for i in range(len(spl), 0, -1):
            yield '.'.join(spl[0:i])
        if module_name:
            yield ''

    @classmethod
    def _get_namespace(mcs, module_name):
        for parent in mcs._module_parents(module_name):
            entry = mcs._default_namespace_dict.get(parent)
            if entry:
                return entry
            
        return '' # Default if nothing specified




