import copy 
import logging
import sys

import whispers
from whispers.exceptions import NotifierException

class NotificationHandler(logging.Handler):
    """A :class:`logging.Handler` that enables directly sending log messages 
    to notifiers
    
    Arguments:
        logging {[type]} -- [description]
    """

    def __init__(self, provider: str, defaults: dict = None, **kwargs):
        """Sets ups the handler
        
        Arguments:
            provider {str} -- Provider name to use

        :param kwargs: Additional kwargs

        Keyword Arguments:
            defaults {dict} -- Default provider data to use. (default: {None})
        """

        self.defaults = defaults or {}
        self.provider = None
        self.fallback = None
        self.fallback_defaults = None

        self.init_providers(provider, kwargs)

        super().__init__(**kwargs)

    def init_providers(self, provider, kwargs):
        """Inits main and fallback provider if relevant.
        
        Arguments:
            provider {[type]} -- Provider name to use
            kwargs {[type]} -- Additional kwargs
        
        :raises ValueError: If provider name or fallback names are not valid providers
        """

        self.provider = whispers.get_notifier(provider, strict=True)

        if kwargs.get("fallback"):
            self.fallback = whispers.get_notifier(kwargs.pop("fallback"), strict=True)
            self.fallback_defaults = kwargs.pop("fallback_defaults", {})

    def emit(self, record):
        """Override the "meth:`~logging.Handler.emit` method that takes the ``msg`` attribute from the log record passed
        
        Arguments:
            record {[type]} -- :class:`logging.LogRecord`
        """

        data = copy.deepcopy(self.defaults)
        data["message"] = self.format(record)

        try:
            self.provider.notify(raise_on_errors = True, **data )
        except Exception:
            self.handleError(record)

    def __repr__(self):
        level = logging.getLevelName(self.level)
        name = self.provider.name

        return "<%s %s(%s)" % (self.__class__.__name__, name, level)

    def handleError(self, record): 
        """Handles any errors raised during the :meth:`emit` method. Will only try to pass exception to fallback notifier
        (if defined) in case the exception is a sub-class of :exc:`~whispers.exceptions.NotifierException`. 
        
        Arguments:
            record {[type]} -- :class:`logging.LogRecord`        
        """

        if logging.raiseExceptions:
            t, v, tb = sys.exc_info()
            if issubclass(t, NotifierException) and self.fallback:
                msg = f"Could not log msg to provider '{self.provider.name}'!\n{v}"
                self.fallback_defaults["message"] = msg
                self.fallback.notify(**self.fallback_defaults)
            else: 
                super().handleError(record)



