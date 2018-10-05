import logging
from abc import ABC, abstractmethod

import jsonschema
import requests
from jsonschema.exceptions import best_match 

from .exceptions import (
    SchemaError, 
    BadArguments,
    NotificationError,
    NoSuchNotifierError,
)

from .utils.helpers import merge_dicts, dict_from_environs
from .utils.schema.formats import format_checker

DEFAULT_ENVIRON_PREFIX = "NOTIFIERS_"

log = logging.getLogger("whispers")

FAILURE_STATUS = "Failure"
SUCCESS_STATUS = "Success"

class Response:
    def __init__(
        self, status: str, provider: str, data: dict, response: requests.Response = None,
        errors: list = None,
    ):
        self.status = status
        self.provider = provider
        self.data = data
        self.response = response
        self.errors = errors

    def __repr__(self):
        return f"<Response,provider={self.provider.capitalize()}, status={self.status}, errors={self.errors}>"

    def raise_on_errors(self):
        if self.errors:
            raise NotificationError(
                provider=self.provider,
                data=self/data,
                errors=self.errors,
                response=self.response,
            )

    @property
    def ok(self):
        return self.errors is None

class SchemaResource(ABC):
    """Base class that represents an object schema and its utility methods
    
    Arguments:
        ABC {[type]} -- [description]
    
    Raises:
        SchemaError -- [description]
        BadArguments -- [description]
    
    Returns:
        [type] -- [description]
    """

    @property
    @abstractmethod
    def _required(self) -> dict:
        pass

    @property
    @abstractmethod
    def _schema(self) -> dict:
        pass

    _merged_schema = None

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def schema(self) -> dict:
        if not self._merged_schema:
            log.debug("merging required dict into schema for %s", self.name)

            self._merged_schema = self._schema.copy()
            self._merged_schema.update(self._required)

        return self._merged_schema

    @property
    def arguments(self) -> dict:
        return dict(self.schema["properties"].items())

    @property
    def required(self) -> dict:
        return self._required

    def create_response(
        self, data: dict = None, response: requests.Response = None, errors: list = None
        ) -> Response: 
        status = FAILURE_STATUS if errors else SUCCESS_STATUS

        return Response(
            status = status, provider = self.name, data = data, 
            response = response, errors = errors,
        )

    def _merge_defaults(self, data: dict) -> dict:
        log.debug("merging defaults %s into data %s", self.defaults, data)

        return merge_dicts(data, self.defaults)

    def _get_environs(self, prefix: str = None) -> dict:
        if not prefix:
            log.debug("using default environ prefix")
            prefix = DEFAULT_ENVIRON_PREFIX

        return dict_from_environs(prefix, self.name, list(self.arguments.keys()))

    def _prepare_data(self, data: dict) -> dict:
        """
        Use this method to manipulate data that will fit the respected provider API.
         For example, all providers use the ``message`` argument but sometimes
         provider expects a different variable name for this, like ``text``.

         :param data: Notification data
         :return: Returns manipulated data, if there is a need
        """       

        return data

    def _validate_schema(self):
        """
        Validates provider schema for syntax issues. Raises :class:`~notifiers.exceptions.SchemaError` if relevant

        :raises: :class:`~notifiers.exceptions.SchemaError`
        """
        try:
            log.debug("validating provider schema")
            self.validator.check_schema(self.schema)
        except jsonschema.SchemaError as e:
            raise SchemaError(
                schema_error=e.message, provider=self.name, data=self.schema
            )

    def _validate_data(self, data: dict):
        """
        Validates data against provider schema. Raises :class:`~notifiers.exceptions.BadArguments` is relevant
        
        Arguments:
            data {dict} -- Data to validate

        :raises: :class:`~notifiers.exceptions.BadArguments`
        """
        log.debug("validating provided data")
        
        e = best_match(self.validator.iter_errors(data))

        if e:
            custom_error_key = f"error_{e.validator}"

            msg = (
                e.schema[custom_error_key]
                if e.schema.get(custom_error_key)
                else e.message
            )

            raise BadArguments(validation_error=msg, provider=self.name, data=data)

    def _validate_data_dependencies(self, data: dict) -> dict:
        return data

    def _process_data(self, **data) -> dict:
        env_prefix = data.pop("env_prefix", None)
        environs = self._get_environs(env_prefix)

        if environs:
            data = merge_dicts(data, environs)

        data = self._merge_defaults(data)
        self._validate_data(data)
        data = self._validate_data_dependencies(data)
        data = self._prepare_data(data)

        return data

    def __init__(self):
        
        self.validator = jsonschema.Draft4Validator(
            self.schema, format_checker = format_checker
        )

        self._validate_schema()

class Provider(SchemaResource, ABC):
    _resources = {}

    def __repr__(self):
        return f"<Provider:[{self.name.capitalize()}]>"

    def __getattr__(self, item):
        if item in self._resources:
            return self._resources[item]

        raise AttributeError(f"{self} does not have a property {item}")

    @property
    @abstractmethod
    def base_url(self):
        pass

    @property
    @abstractmethod
    def site_url(self):
        pass

    @property
    def metadata(self) -> dict:
        return {"base_url": self.base_url, "site_url": self.site_url, "name": self.name}

    @property
    def resources(self) -> list:
        """Return a list of names of relevant :class:`~notifiers.core.ProviderResource` objects"""
        return list(self._resources.keys())

    @abstractmethod
    def _send_notification(self, data: dict) -> Response:
        """The core method to trigger the provider notification. Must be overriden.

        Arguments:
            data {dict} -- Notification data
        
        Returns:
            Response -- [description]
        """
        pass

    def notify(self, raise_on_errors: bool = False, **kwargs) -> Response:
        """
        The main method to send notification. Prepare the data via the 
        :meth:`~notifiers.core.SchemaResource._prepare_data` method 

        :param: kwargs: Notification data
        :param: raise_on_errors: Should the meth:`~notifiers.core.Response.raise_on_errors` be invoked immediately
        
        :raises: :class:`~notifiers.exceptions.NotificationError` if ``raise_on_errors`` is set to True 
         and response contained errors

        Keyword Arguments:
            raise_on_errors {bool} -- [description] (default: {False})
        
        Returns:
            Response -- A :class:`~notifiers.core.Response` object
        """

        data = self._process_data(**kwargs)
        rsp = self._send_notification(data)

        if raise_on_errors:
            rsp.raise_on_errors()

        return rsp

class ProviderResource(SchemaResource, ABC):
    """ 
    The base class that is used to fetch provider realted resources 
    like rooms, channels, users etc.
    """ 
    @property
    @abstractmethod
    def resource_name(self):
        pass

    @abstractmethod
    def _get_resource(self, data: dict):
        pass

    def __call__(self, **kwargs):
        data = self.process_data(**kwargs)
        return self._get_resource(data)

    def __repr__(self):
        return f"<ProviderResourse,provider={self.name},resource={self.resource_name}>"

# Avoid premature import 
from .providers import _all_providers

def get_notifier(provider_name: str, strict: bool = False) -> Provider:
    """Convenience method to return the an instantiated :class:`~whispers.core.Provider` object according to `name`
    
    Arguments:
        provider_name {str} -- The `name` of the requested :class:`~whispers.core.Provider`
    
    Keyword Arguments:
        strict {bool} -- Raises a :class:`ValueError` if the given provider string was not found (default: {False})
    
    Returns:
        Provider -- :class:`Provider` or None

    :raises ValueError: In case of `strict` is True and provider not found
    """

    if provider_name in _all_providers:
        log.debug("found a match for %s, returning", provider_name)
        return _all_providers[provider_name]()
    elif strict:
        raise NoSuchNotifierError(name=provider_name)

def all_providers() -> list:
    """Returns a list of all :class:`~whispers.core.Provider` names
    
    Returns:
        list -- [description]
    """
    
    return list(_all_providers.keys())

def notify(provider_name: str, **kwargs) -> Response:
    """Quickly sends a notification without needing to get a notifier via the :func:`get_notifier` method.

    :param provider_name: Name of the notifier to use. Note that if this notifier name does not exist it will raise an exception.
    :param kwargs: Notification data, dependent on provider
    :return: :class:Response
    :raises: :class:`~whispers.exceptions.NoSuchNotifierError` if `provider_name` is unknown
    """

    return get_notifier(provider_nane=provider_name, strict=True).notify(**kwargs)

