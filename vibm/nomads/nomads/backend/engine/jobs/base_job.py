import abc

"""
Abstract base class that containes only most interesting functionality.
"""
class BaseJob(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def prepare(self):
        raise NotImplementedError( "Users Must Define 'prepare() to Use this Base Class" )
        
    @abc.abstractmethod
    def start(self):
        raise NotImplementedError( "Users Must Define 'start()' to Use this Base Class" )

    @abc.abstractmethod
    def stop(self):
        raise NotImplementedError( "Users Must Define 'stop()' to Use this Base Class" )