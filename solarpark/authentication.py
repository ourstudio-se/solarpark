from typing import Dict

import jwt
from fastapi import HTTPException, Request
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer

from solarpark.settings import settings


async def decode_jwt(auth: HTTPAuthorizationCredentials) -> Dict:
    try:
        jwks_url = f"https://{settings.DOMAIN}/.well-known/jwks.json"
        jwks_client = jwt.PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(auth.credentials).key
        return jwt.decode(
            auth.credentials,
            signing_key,
            algorithms=settings.ALGORITHMS,
            audience=settings.API_AUDIENCE,
            issuer=settings.ISSUER,
            options={"verify_exp": True, "verify_signature": True},
        )
    except jwt.ExpiredSignatureError as ex:
        raise HTTPException(403) from ex
    except Exception as ex:
        raise HTTPException(401) from ex


class Authorizer(HTTPBearer):
    def __init__(self, http_bearer: HTTPBearer):
        self.http_bearer = http_bearer
        self.model = http_bearer.model
        self.scheme_name = http_bearer.scheme_name

    async def __call__(self, request: Request):
        http_auth = await self.http_bearer(request)
        if http_auth is None:
            raise HTTPException(401)

        data = await decode_jwt(http_auth)

        if "solarpark-admin" in data.get("permissions", None):
            return http_auth
        if "solarpark-read" in data.get("permissions", None) and request.method == "GET":
            return http_auth

        raise HTTPException(401)


api_security = Authorizer(HTTPBearer())
