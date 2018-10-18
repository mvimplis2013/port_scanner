from cc.environment import Environment

__author__ = 'John.Who'

class StandardEnvironment(Environment):
    def is_auth_enabled(self):
        return False

    def get_auth_users(self):
        return []
