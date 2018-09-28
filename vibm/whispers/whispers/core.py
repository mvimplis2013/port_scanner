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

class SchemaResourse(ABC):
    @property
    @abstractmethod
    def _required(self) -> dict:
        pass

    @property
    @abstractmethod
    def _schema(self) -> dict:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def schema(self) -> dict:
        if not self._merged_schema:
            log.debug("merging required dict into schema for %s", self.name)

            self._merged_schema = self._schema_copy()
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

    def validate_data(self, data: dict):
        """
        Validates data against provider schema. Raises :class:`~notifiers.exceptions.BadArguments` is relevant
        
        Arguments:
            data {dict} -- Data to validate

        :raises: :class:`~notifiers.exceptions.BadArguments`
        """
        log.debug("validating provider data")
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

        data = self.merge_defaults(data)
        self._validate_data(data)
        data = self._validate_data_dependencies(data)
        data = self._prepare_data(data)

        return data

    def __init__(self):
        self.validator = jsonschema.Draft4Validator(
            self.schema, format_checker = format_checker
        )

        self.validate_schema()

class Provider(SchemaResourse, ABC):
    _resources = {}

    def __repr__(self):
        return f"<Provider:[{self.name.capitalize()}]>"

    def __getattr__(self, item):
        if item in self._resources:
            return self.resources[item]

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

def entry_point():
    exit(1)

if __name__ == "__main__":
    entry_point()