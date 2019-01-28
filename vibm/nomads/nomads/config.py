import os 

PATH = "NOMADS_PATH"

class Config(object):
    def __init__(self):
        if PATH in os.environ:
            pass
        else:
            raise EnvironmentError("Base Path Not Set")

        self.nomads_path = os.environ.get(PATH)

if __name__ == "__main__":
    config = Config()
