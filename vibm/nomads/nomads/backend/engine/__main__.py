from . import nomads_logger
from . import TomlParser 
from . import Configurator
from . import DatabaseManager

from . import Scheduler

from .back_robot import BackRobot 

toml_parser = TomlParser.instance()

configurator = Configurator( toml_parser )
print( configurator.external_monitoring )

print( toml_parser.get("external-monitoring", "vlabs"))
robot = BackRobot()

database_manager = DatabaseManager()
database_manager.select_external_targets()

# schedule_monitoring_for_every_external_server()
scheduler = Scheduler()
scheduler.scheduleExternalServersPing()