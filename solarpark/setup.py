from fastapi import Depends

from solarpark.api import members, shares
from solarpark.logging import get_logger


def add_routes(app) -> None:
    app.include_router(
        members.router,
        tags=["members"],
        dependencies=[Depends(get_logger)],
    )
    app.include_router(
        shares.router,
        tags=["shares"],
        dependencies=[Depends(get_logger)],
    )
