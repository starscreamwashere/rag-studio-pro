"""Clerk JWT verification.

Verifies the session token the frontend attaches as a Bearer token: signature
is checked against Clerk's JWKS (RS256), plus issuer and expiry. The verified
``sub`` claim is the Clerk user id.
"""

from functools import lru_cache

import jwt
from jwt import PyJWKClient

from app.core.config import settings


class AuthError(Exception):
    """Raised when a token cannot be verified."""


@lru_cache
def _jwk_client() -> PyJWKClient:
    if not settings.clerk_jwks_uri:
        raise AuthError("Clerk is not configured (missing publishable key / JWKS URL).")
    return PyJWKClient(settings.clerk_jwks_uri)


def verify_clerk_token(token: str) -> dict:
    """Verify a Clerk session JWT and return its claims."""
    try:
        signing_key = _jwk_client().get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.clerk_issuer_url,
            options={"verify_aud": False},
            leeway=5,
        )
    except AuthError:
        raise
    except jwt.PyJWTError as exc:
        raise AuthError(f"Invalid token: {exc}") from exc
