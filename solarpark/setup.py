from fastapi import Depends

from solarpark.api import members, shares
from solarpark.authentication import api_security
from solarpark.logging import get_logger


def add_routes(app) -> None:
    app.include_router(
        members.router,
        tags=["members"],
        dependencies=[Depends(get_logger), Depends(api_security)],
    )
    app.include_router(
        shares.router,
        tags=["shares"],
        dependencies=[Depends(get_logger), Depends(api_security)],
    )
