"""Error base file."""


class Error(Exception):
    """Base class for other exceptions."""

    def __init__(self, error_code=None, error_type=None):
        """Initialize base error properties."""
        self.error_code = error_code
        self.error_type = error_type


class EndpointNotImplementedError(Error):
    """Error raised when trying to access a method not yet implemented."""

    def __init__(self):
        """Initialize base error properties."""
        self.error_code = "ENDPOINT_NOT_YET_IMPLEMENTED"
        self.error_type = "FORBIDDEN"


class ApiError(Exception):
    """Error raise when something wrong happened at Olyn API servers."""

    def __init__(self, error_code=None, error_type=None, traceback_id=None):
        """Initialize base error properties."""
        self.error_code = error_code
        self.error_type = error_type
        self.traceback_id = traceback_id


class RequestValidationError(Error):
    """Error raised when a request is bad formatted."""

    pass


class UnauthorizedError(Error):
    """Error raised when trying to access a resource without authentication."""

    pass


class ForbiddenError(Error):
    """Error raised when trying to access a resource without authorization."""

    pass


class NotFoundError(Error):
    """Error raised when a resource is not found in Olyn API."""

    pass


class MethodNotAllowedError(Error):
    """Error raised when a resource is not found in Olyn API."""

    pass


class ConflictError(Error):
    """Error raised when state from current resources mismatch."""

    pass
