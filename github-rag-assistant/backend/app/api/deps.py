"""Shared FastAPI dependencies. Auth is wired here but not enforced yet."""
from typing import Optional

from fastapi import Header

from app.core.security import CurrentUser, decode_token


def get_current_user(authorization: Optional[str] = Header(default=None)) -> CurrentUser:
    """Every protected route should depend on this.

    Today it always resolves to an anonymous user. Once auth is enabled,
    this is the only function that needs to change.
    """
    token = authorization.split(" ")[-1] if authorization else None
    return decode_token(token)
