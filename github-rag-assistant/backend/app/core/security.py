"""
Placeholder for future authentication.

Nothing here is enforced yet. When auth is added, wire OAuth2PasswordBearer
(or a JWT/session scheme) here and have `decode_token` raise on invalid
credentials. Every route already depends on `get_current_user` via
`app/api/deps.py`, so enabling auth later is a one-file change.
"""
from typing import Optional


class CurrentUser:
    """Minimal user placeholder. Replace with a real user model later."""

    def __init__(self, user_id: str = "anonymous"):
        self.user_id = user_id


def decode_token(token: Optional[str]) -> CurrentUser:
    """Stub: currently returns an anonymous user regardless of token.

    Replace with real JWT/session verification when auth is introduced,
    e.g. jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"]).
    """
    return CurrentUser()
