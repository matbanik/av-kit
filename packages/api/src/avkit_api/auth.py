"""Dual Bearer authentication against `AUTH_TOKENS`."""

from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.requests import Request

_bearer = HTTPBearer(auto_error=False)


def require_bearer(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> None:
    """Reject missing or unknown Bearer tokens with 401 + `WWW-Authenticate`."""
    tokens: frozenset[str] = request.app.state.tokens
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    matched = False
    supplied = credentials.credentials
    for token in tokens:
        if secrets.compare_digest(supplied, token):
            matched = True
    if not matched:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
