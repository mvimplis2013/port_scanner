import os.path

try:
    import toml
except ImportError:
    toml = False

from .base_parser import BaseParser

class FinestrinoTomlParser(BaseParser):
    NO_DEFAULT = object()
    enabled = bool(toml)
    data = dict()

    _instance = None
    _config_paths = [
        '/etc/finestrino/finestrino.toml',
        'finestrino.toml'
    ]    

    @staticmethod
    def _update_data(data, new_data):
        print('Inside Update Data')
        if not new_data:
            return data
        if not data:
            return new_data
        
        for section, content in new_data.items():
            if section not in data:
                data[section] = dict()
            
            data[section].update(content)

        return data

    def read(self, config_paths):
        print('Someone called me')
        self.data = dict()

        for path in config_paths:
            print('Path is ...', path)
            if os.path.isfile(path):
                self.data = self._update_data(self.data, toml.load(path))

        return self.data

    def get(self, section, option, default=NO_DEFAULT, **kwargs):
        try:
            return self.data[section][option]
        except KeyError:
            if default is self.NO_DEFAULT:
                raise

            return default
    
    def getboolean(self, section, option, default=NO_DEFAULT):
        return self.get(section, option, default)

    def getint(self, section, option, default=NO_DEFAULT):
        return self.get(section, option, default)

    def getfloat(self, section, option, default=NO_DEFAULT):
        return self.get(section, option, default)

    def getindict(self, section):
        return self.data.get(section, {})

    def set(self, section, option, value=None):
        if section not in self.data:
            self.data[section] = []

        self.data[section][option] = value

    def __getitem(self, name):
        return self.data[name]
 
