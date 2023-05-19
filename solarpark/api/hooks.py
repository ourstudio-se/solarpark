# pylint: disable=W0101, W0105
from typing import Dict

from fastapi import APIRouter

router = APIRouter()


@router.post("/hooks/email", summary="Incoming email webhooks")
async def email_hook(request: Dict):  # body: Dict
    print(request["envelop"]["from"])
    return None

    """
    Used by email-to-webhook service for incoming emails

    1. Parse json with form data
    2. Create lead from form data
    """
    # get_logger().info(f"received email hook: {body}")
