from fastapi import Depends

from solarpark.api import admin, analytics, hooks, members, shares
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
    app.include_router(
        analytics.router,
        tags=["analytics"],
        dependencies=[Depends(get_logger), Depends(api_security)],
    )
    app.include_router(
        admin.router,
        tags=["admin"],
        dependencies=[Depends(get_logger), Depends(api_security)],
    )
    app.include_router(
        hooks.router,
        tags=["hooks"],
        dependencies=[Depends(get_logger), Depends(api_security)],
    )
