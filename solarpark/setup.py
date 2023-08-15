from fastapi import Depends

from solarpark.api import admin, analytics, economics, generate, hooks, leads, members, send_email, shares
from solarpark.authentication import api_security
from solarpark.logging import get_logger


def add_routes(app) -> None:
    app.include_router(
        economics.router,
        tags=["economics"],
        dependencies=[Depends(api_security)],
    )
    app.include_router(
        send_email.router,
        tags=["send_email"],
        dependencies=[Depends(get_logger), Depends(api_security)],
    )
    app.include_router(
        generate.router,
        tags=["generate"],
        dependencies=[Depends(get_logger), Depends(api_security)],
    )
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
        leads.router,
        tags=["leads"],
        dependencies=[Depends(get_logger), Depends(api_security)],
    )
    app.include_router(
        hooks.router,
        tags=["hooks"],
        dependencies=[Depends(get_logger)],
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
