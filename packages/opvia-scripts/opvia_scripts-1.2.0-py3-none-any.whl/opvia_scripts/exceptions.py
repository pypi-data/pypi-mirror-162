class OpviaScriptsException(Exception):
    """
    Abstract exception for opvia scripts exceptions
    """


class MalformedObject(OpviaScriptsException):
    """
    Raised when there's a schema validation problem on a custom validator
    """


class MissingEntity(OpviaScriptsException):
    """
    Raised when there's a required entity that wasn't provided by a client
    """
