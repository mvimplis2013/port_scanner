class Item(object):
    properties = {
        'imported_from': StringProp(default='unknown'),
        'use': ListProp(default=None, split_on_coma=True),
    }

    running_properties = {
        'configuration_warnings': ListProp(default=[]),
        'configuration_errors': ListProp(default=[]),
    }

    def __init__(self, params={}):

    def init_running_properties(self):
        for prop, entry in self.__class__.running_properties.items():
            val = entry.default
            if hasattr(val, '__iter__'):
                setattr(self, prop, copy(val))
            else:
                setattr(self, val)

    # We load every useful parameter so we need to access global conf later.
    # Must be called after a change in a global conf parameter.
    def load_global_conf(cls, conf):
        for prop, entry in conf.properties.