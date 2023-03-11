from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solarpark.api import parse_integrity_error_msg
from solarpark.models.shares import Share, ShareCreateRequest
from solarpark.persistence.database import get_db
from solarpark.persistence.shares import create_share, get_share

router = APIRouter()


@router.get("/shares/{share_id}", summary="Get specific share")
async def get_share_endpoint(share_id: int, db: Session = Depends(get_db)) -> Share:
    share = get_share(db, share_id)
    if not share:
        raise HTTPException(status_code=404, detail="share not found")
    return share


@router.post("/shares", summary="Create share")
async def create_share_endpoint(share_request: ShareCreateRequest, db: Session = Depends(get_db)) -> Share:
    try:
        return create_share(db, share_request)
    except IntegrityError as ex:
        if "UniqueViolation" in str(ex):
            raise HTTPException(status_code=400, detail=parse_integrity_error_msg("Key (.*?) exists", str(ex))) from ex
        if "violates foreign key" in str(ex):
            raise HTTPException(
                status_code=400, detail=parse_integrity_error_msg("Key (.*?) not present", str(ex))
            ) from ex
    raise HTTPException(status_code=400, detail="error creating share")
