"""
Amazon Cognito integration — optional; used when COGNITO_USER_POOL_ID is configured.
Provides token verification as an alternative to local JWT.
"""
import logging
from functools import lru_cache
from typing import Optional

import requests
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode

from app.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_jwks() -> dict:
    """Fetch and cache the Cognito JWKS (JSON Web Key Set)."""
    url = (
        f"https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com/"
        f"{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    )
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()


def verify_cognito_token(token: str) -> Optional[dict]:
    """
    Verify a Cognito JWT and return its claims dict, or None if invalid.

    Steps:
    1. Decode token header to get kid
    2. Find matching key in JWKS
    3. Verify signature and claims
    """
    if not settings.COGNITO_USER_POOL_ID:
        return None

    try:
        # Decode header without verification to extract kid
        headers = jwt.get_unverified_headers(token)
        kid = headers.get("kid")

        jwks = _get_jwks()
        key_data = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key_data:
            logger.warning("Cognito: no matching key found for kid=%s", kid)
            return None

        public_key = jwk.construct(key_data)
        message, encoded_sig = token.rsplit(".", 1)
        decoded_sig = base64url_decode(encoded_sig.encode("utf-8"))

        if not public_key.verify(message.encode("utf-8"), decoded_sig):
            logger.warning("Cognito: signature verification failed")
            return None

        claims = jwt.get_unverified_claims(token)

        # Verify issuer
        expected_issuer = (
            f"https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com/"
            f"{settings.COGNITO_USER_POOL_ID}"
        )
        if claims.get("iss") != expected_issuer:
            logger.warning("Cognito: issuer mismatch")
            return None

        # Verify audience
        if claims.get("client_id") != settings.COGNITO_CLIENT_ID:
            logger.warning("Cognito: client_id mismatch")
            return None

        return claims

    except (JWTError, Exception) as exc:
        logger.debug("Cognito token verification failed: %s", exc)
        return None


def extract_user_id_from_cognito_token(token: str) -> Optional[str]:
    """Return the 'sub' claim (Cognito user ID) from a valid token."""
    claims = verify_cognito_token(token)
    if claims:
        return claims.get("sub")
    return None
