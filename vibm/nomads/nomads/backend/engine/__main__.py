from . import nomads_logger
from . import TomlParser 
from . import Configurator
from . import DatabaseManager

from .back_robot import BackRobot 

toml_parser = TomlParser.instance()

configurator = Configurator( toml_parser )
print( configurator.external_monitoring )

print( toml_parser.get("external-monitoring", "vlabs"))
robot = BackRobot()

database_manager = DatabaseManager()