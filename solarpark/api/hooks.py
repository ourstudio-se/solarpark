# pylint: disable=W0101, W0105

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from structlog import get_logger

from solarpark.api import parse_integrity_error_msg
from solarpark.models.leads import Lead
from solarpark.persistence.database import get_db
from solarpark.persistence.hooks import commit_email_hook

router = APIRouter()


@router.post("/hooks/email", summary="Incoming email webhooks")
async def email_hook(request: Dict, db: Session = Depends(get_db)) -> Lead:
    try:
        return commit_email_hook(db, request)
    except IntegrityError as ex:
        print(ex)
        get_logger().error(f"error commiting email hook: {ex}")

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
