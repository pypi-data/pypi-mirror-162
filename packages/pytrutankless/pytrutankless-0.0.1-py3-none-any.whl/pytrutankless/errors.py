"""Define package errors."""

class TruTanklessError(Exception):
    """A base error."""

    pass

class InvalidCredentialsError(TruTanklessError):
    """An error related to invalid requests."""

    pass

class InvalidResponseFormat(TruTanklessError):
    """An error related to invalid requests."""

    pass

class GenericHTTPError(TruTanklessError):
    """An error related to invalid requests."""

    pass