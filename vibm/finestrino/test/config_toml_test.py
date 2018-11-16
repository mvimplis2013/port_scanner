from finestrino.configuration import FinestrinoTomlParser, get_config, add_config_path

class TomlConfigParserTest:
    @classmethod
    def setUpClass(cls):
        add_config_path('test/testconfig/finestrino.toml')
        add_config_path('test/testconfig/finestrino_local.toml')

    def setUp(self):
        FinestrinoTomlParser._instance = None
        

    def test_get_config(self):
        config = get_config('toml')
        print('Get Config ', config.data)
        print( config.get('hdfs', 'client') ) 

if __name__ == '__main__':
    print('Testing Toml')     
    a = TomlConfigParserTest()
    a.setUpClass()
    #a.setUp()
    a.test_get_config()
