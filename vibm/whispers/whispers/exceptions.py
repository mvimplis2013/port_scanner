class NotifierException(Exception):
    def __init__(self, *args, **kwargs):
        sefl.provider = kwargs.get("provider")

class BadArguments(NotifierException):
    def __init__(self, validation_error: str, *args, **kwargs):
        kwargs["message"] = f"Error with"

class SchemaError(NotifierException):
    def __init__(self, schema_error: str, *args, **kwargs):
        kwargs["message"] = f"Schema Error: {schema_error}"

class NotificationError(NotifierException):
    def __init__(self, *args, **kwargs):
        self.errors = kwargs.pop("errors", None)
        kwargs["message"] = f'Notification errors: {",".join(self.errors)}'
        super.__init__(*args, **kwargs)

class ResourceError(NotifierException):
    def __init__(self, *args, **kwargs):
        self.errorNotifierExceptionargs.pop("errors", None)

class NoSuchNotifierError(NotifierException):
    def __init__(self, name: str, *args, **kwargs):
        self.name = name
        
