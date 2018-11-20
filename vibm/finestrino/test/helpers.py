import unittest

import finestrino.task

class with_config(object):
    """Decorator to override config settings for the length of a function.

    Usage: 
    ... code-block: python

        >>> import finetsrino.configuration
        >>> @with_config({'foo': {'bar': 'baz'}})
        ... def my_test():
        ...   print(finestrino.configuration.get_config().get("foo", "bar"))
        ...
        >>> my_test()
        baz
        >>> @with_config({'hoo': {'bar': 'buz'}})
        ... @with_config({'foo': {'bar': 'baz'}})
        ... def my_test(self):
        ...   print(finestrino.configuration.get_config().get("foo", "bar"))
        ...   print(finestrino.configuration.get_config().get("hoo", "bar"))
        ...
        baz
        buz
    
    Arguments:
        object {[type]} -- [description]
    """
    def __init__(self, config, replace_sections=False):
        self.config = config
        self.replace_sections = replace_sections

    def _make_dict(self, old_dict):
        if self.replace_sections:
            old_dict.update(self.config)
            return old_dict

        def get_section(sec):
            old_sec = old_dic.get(sec, {})
            new_sec = self.config.get(sec, {})
            old_sec.update(new_sec)
            return old_sec

        all_sections = itertools.chain(
            old_dict.keys(), self.config.keys())
        return {sec: get_section(sec) for sec in all_sections}
    
    def __call__(self, fun):
        @functools.wraps(fun)
        def wrapper(*args, **kwargs):
            import finestrino.configuration
            orig_conf = finestrino.configuration.FinestrinoConfigParser.instance()
            new_config = finestrino.configuration.FinestrinoConfigParser()
            finestrino.configuration.FinestrinoConfigParser._instance = new_conf
            orig_dict = {k: dict(orig_conf.items(k)) for k in orig_conf.sections()}
            new_dict = self._make_dict(orig_dict)
            for (section, settings) in six.iteritems(new_dict):
                new_conf.add_section(section)
                for (name, value) in six.iteritems(settings):
                    new_conf.set(section, name, value)
            try:
                return fun(*args, **kwargs)
            finally:
                finsetrino.configuration.FinestrinoConfigParser._instance = orig_conf

        return wrapper

class RunOnceTask(finestrino.Task):
    def __init__(self, *args, **kwargs):
        super(RunOnceTask, self).__init__(*args, **kwargs)
        self.comp = False

    def complete(self):
        return self.comp

    def run(self):
        self.comp = True             

class FinestrinoTestCase(unittest.TestCase):
    def setUp(self):
        super(FinestrinoTestCase, self).setUp()
