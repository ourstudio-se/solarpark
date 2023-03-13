from fastapi import HTTPException, Request
from fastapi.security.http import HTTPBearer

from solarpark.settings import settings


class Authorizer(HTTPBearer):
    def __init__(self, http_bearer: HTTPBearer):

        self.http_bearer = http_bearer
        self.model = http_bearer.model
        self.scheme_name = http_bearer.scheme_name

    async def __call__(self, request: Request):
        http_auth = await self.http_bearer(request)
        if http_auth is None:
            raise HTTPException(401)

        if http_auth.credentials == settings.API_KEY:
            return

        raise HTTPException(403, "Unauthorized access")


api_security = Authorizer(HTTPBearer())
