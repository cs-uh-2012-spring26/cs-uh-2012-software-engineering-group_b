from app.exceptions import (
    AuthorizationError,
    DomainError,
    InfrastructureError,
    NotFoundError,
    ValidationError,
)


def test_validation_error_status():
    error = ValidationError("invalid")
    assert error.status_code == 400


def test_authorization_error_status():
    error = AuthorizationError("forbidden")
    assert error.status_code == 403


def test_not_found_error_status():
    error = NotFoundError("missing")
    assert error.status_code == 404


def test_domain_error_status():
    error = DomainError("conflict")
    assert error.status_code == 409


def test_infrastructure_error_status():
    error = InfrastructureError("dependency failed")
    assert error.status_code == 502
