class UserException(Exception):
    """Exception raised when the error is due to the user."""

    pass


class UserValueError(ValueError, UserException):
    """Exception raised when the user provides a wrong value."""

    pass


class UserTypeError(TypeError, UserException):
    """Exception raised when the user provides a value with the wrong type."""

    pass


class UserRuntimeError(RuntimeError, UserException):
    """Exception raised when the error in runtime is due to the user."""

    pass
