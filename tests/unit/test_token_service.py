from app.services.token_service import TokenService


def test_resolve_role_valid_token():
    assert TokenService.resolve_role("trainer-secret-123") == "trainer"


def test_resolve_role_invalid_token():
    assert TokenService.resolve_role("invalid-token") is None


def test_is_valid_token():
    assert TokenService.is_valid("admin-secret-456") is True
    assert TokenService.is_valid("unknown") is False
