import unittest

from finestrino.configuration import FinestrinoTomlParser, get_config, add_config_path
from helpers import FinestrinoTestCase

class TomlConfigParserTest(FinestrinoTestCase):
    @classmethod
    def setUpClass(cls):
        add_config_path('test/testconfig/finestrino.toml')
        add_config_path('test/testconfig/finestrino_local.toml')

    def setUp(self):
        FinestrinoTomlParser._instance = None
        super(TomlConfigParserTest, self).setUp()
        
        

    def test_get_config(self):
        config = get_config('toml')
        print('Get Config ', config.data)
        print( config.get('hdfs', 'client') ) 

class HelpersTest(FinestrinoTestCase):
    def test_add_without_install(self):
        enabled = FinestrinoTomlParser.enabled
        FinestrinoTomlParser.enabled = False
        
# Toplevel script environment
# A module can discover whether or not it is running in the main scope by checking its own __name__, 
# which allows a common idiom for conditionally executing code in a module when it is run as a script or 
# with python -m
if __name__ == '__main__':
    #FinestrinoTomlParser.enabled = True
    TomlConfigParserTest.setUpClass()
    unittest.main()
