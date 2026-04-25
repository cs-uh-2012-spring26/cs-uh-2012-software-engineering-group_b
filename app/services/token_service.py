class TokenService:
    """Resolve registration invite tokens to roles."""

    _VALID_TOKENS = {
        "trainer-secret-123": "trainer",
        "admin-secret-456": "admin",
    }

    @classmethod
    def resolve_role(cls, token: str) -> str | None:
        return cls._VALID_TOKENS.get(token)

    @classmethod
    def is_valid(cls, token: str) -> bool:
        return token in cls._VALID_TOKENS
