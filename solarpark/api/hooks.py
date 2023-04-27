from typing import Dict

from fastapi import APIRouter
from structlog import get_logger

router = APIRouter()


@router.post("/hooks/email", summary="Incoming email webhooks")
async def email_hook(body: Dict):
    """
    Used by email-to-webhook service for incoming emails

    1. Parse json with form data
    2. Create lead from form data
    """
    get_logger().info(f"received email hook: {body}")
    return
