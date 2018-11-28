def add_metaclass(metaclass):
    """Class decorator for creating a class with a metaclass.
    
    Arguments:
        metaclass {[type]} -- [description]
    """
    def wrapper(cls):
        orig_vars = cls.__dict__.copy()
        slots = orig_vars.get('__slots__')
        if slots is not None:
            if isinstance(slots, str):
                slots = [slots]
            for slots_var in slots:
                orig_vars.pop(slots_var)
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)

        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    
    return wrapper

# if PY3:
string_types = str
def iteritems(d, **kw):
    return iter(d.items(**kw))
