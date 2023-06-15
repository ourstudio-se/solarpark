# pylint: disable=W0101, W0105

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solarpark.api import parse_integrity_error_msg
from solarpark.models.leads import Lead
from solarpark.persistence.database import get_db
from solarpark.persistence.hooks import commit_email_hook

router = APIRouter()


@router.post("/hooks/email", summary="Incoming email webhooks")
async def email_hook(request: Dict, db: Session = Depends(get_db)) -> Lead:
    # get_logger().info(f"received email hook: {}")
    try:
        return commit_email_hook(db, request)
    except IntegrityError as ex:
        if "UniqueViolation" in str(ex):
            raise HTTPException(
                status_code=400,
                detail=parse_integrity_error_msg("Key (.*?) exists", str(ex)),
            ) from ex
        if "violates foreign key" in str(ex):
            raise HTTPException(
                status_code=400,
                detail=parse_integrity_error_msg("Key (.*?) not present", str(ex)),
            ) from ex
        raise HTTPException(status_code=400, detail="error committing lead hook") from ex

    """
    Used by email-to-webhook service for incoming emails

    1. Parse json with form data
    2. Create lead from form data
    """
