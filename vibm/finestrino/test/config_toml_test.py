import unittest
import os

from finestrino.configuration import FinestrinoTomlParser, get_config, add_config_path
from helpers import FinestrinoTestCase

class TomlConfigParserTest(unittest.TestCase):
    def setUp(self):
        FinestrinoTomlParser.enabled = True
        
        # Caution ... finestrino/test
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        
        add_config_path( ROOT_DIR + '/testconfig/finestrino.toml')
        add_config_path( ROOT_DIR + '/testconfig/finestrino_local.toml')

    def test_get_config(self):
        config = get_config('toml')
        print('Get Config ', config.data)
        print( config.get('hdfs', 'client') ) 

#class HelpersTest(FinestrinoTestCase):
#    def test_add_without_install(self):
#        enabled = FinestrinoTomlParser.enabled
#        FinestrinoTomlParser.enabled = False
#        with self.assertRaises(ImportError):
#            add_config_path('test/testconfig/finestrino.toml')
#        FinestrinoTomlParser.enabled = enabled

# Toplevel script environment
# A module can discover whether or not it is running in the main scope by checking its own __name__, 
# which allows a common idiom for conditionally executing code in a module when it is run as a script or 
# with python -m
if __name__ == '__main__':
    #TomlConfigParserTest = TomlConfigParserTest()
    #helpersTest = HelpersTest()
    #helpersTest.run()
    unittest.main()
