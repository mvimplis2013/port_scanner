import os 

PATH = "NOMADS_PATH"
CONFIG = "/config"

ERROR_MSG_BASE_PATH_NOT_ENVVAR = "Base Path Not Set as Environment Variable"
ERROR_MSG_BASE_PATH_NOT_FOLDER = "Base Path Not Found a Folder with this Name"
ERROR_MSG_CONFIG_FOLDER_NOT_FOUND = "The 'config' Subfolder Not Found"

class Config(object):
    def __init__(self):
        if PATH in os.environ:
            pass
        else:
            raise EnvironmentError( ERROR_MSG_BASE_PATH_NOT_ENVVAR )

        # Project's Main Folder
        nomads_path = os.environ.get(PATH)
        if not os.path.exists( nomads_path ):
            # Cannot find the project's main folder
            raise EnvironmentError( ERROR_MSG_BASE_PATH_NOT_FOLDER + "...%s" + PATH)

        # Check "config" subfolder
        config_path = nomads_path + CONFIG
        if not os.path.exists(config_path):
            # Cannot find the "config" subfolder
            raise EnvironmentError( ERROR_MSG_CONFIG_FOLDER_NOT_FOUND )


if __name__ == "__main__":
    config = Config()
