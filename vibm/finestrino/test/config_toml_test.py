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
        self.assertIsInstance(config, FinestrinoTomlParser) 

    def test_file_reading(self):
        config = get_config('toml')
        self.assertIn('hdfs', config.data)

    def test_get(self):
        config = get_config('toml')

        # test getting
        self.assertEqual(config.get('hdfs', 'client'), 'hadoopcli')
        self.assertEqual(config.get('hdfs', 'client', ' test'), 'hadoopcli')

        # test default
        self.assertEqual(config.get('hdfs', 'test', 'check'), 'check')

        with self.assertRaises(KeyError):
            config.get('hdfs', 'test')

        # test override , keys is defined in both .toml files
        self.assertEqual(config.get('hdfs', 'namenode_host'), 'localhost')

        # test non-string values 
        self.assertEqual(config.get('hdfs', 'namenode_port'), 50030)

    def test_set(self):
        config = get_config('toml')

        self.assertEqual(config.get('hdfs', 'client'), 'hadoopcli')
        config.set('hdfs', 'client', 'test')
        self.assertEqual(config.get('hdfs', 'client'), 'test')
        config.set('hdfs', 'check', 'test me')
        self.assertEqual(config.get('hdfs', 'check'), 'test me')

# Toplevel script environment
# A module can discover whether or not it is running in the main scope by checking its own __name__, 
# which allows a common idiom for conditionally executing code in a module when it is run as a script or 
# with python -m
if __name__ == '__main__':
    #TomlConfigParserTest = TomlConfigParserTest()
    #helpersTest = HelpersTest()
    #helpersTest.run()
    unittest.main()
