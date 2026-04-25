class AppError(Exception):
    """Base app exception carrying an HTTP status code."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(AppError):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(message, 400)


class AuthorizationError(AppError):
    """Raised when authorization fails."""

    def __init__(self, message: str):
        super().__init__(message, 403)


class NotFoundError(AppError):
    """Raised when a resource cannot be found."""

    def __init__(self, message: str):
        super().__init__(message, 404)


class DomainError(AppError):
    """Raised when domain/business constraints are violated."""

    def __init__(self, message: str):
        super().__init__(message, 409)


class InfrastructureError(AppError):
    """Raised when an external dependency fails."""

    def __init__(self, message: str):
        super().__init__(message, 502)
