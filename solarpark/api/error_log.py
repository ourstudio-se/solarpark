# pylint: disable=W0622

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solarpark.api import parse_integrity_error_msg
from solarpark.models.error_log import ErrorLog, ErrorLogCreateRequest, ErrorLogs, ErrorLogUpdateRequest, SingleErrorLog
from solarpark.persistence.database import get_db
from solarpark.persistence.error_log import (
    create_error,
    delete_error,
    get_all_errors,
    get_error,
    get_error_by_list_ids,
    update_error,
)

router = APIRouter()


@router.get("/errors/{error_id}", summary="Get error")
async def get_error_endpoint(error_id: int, db: Session = Depends(get_db)) -> SingleErrorLog:
    errors = get_error(db, error_id)

    if len(errors["data"]) != 1:
        raise HTTPException(status_code=404, detail="error not found")

    return {"data": errors["data"][0]}


@router.get("/errors", summary="Get all errors")
async def get_errors_endpoint(
    range: str | None = None,
    sort: str | None = None,
    filter: str | None = None,
    db: Session = Depends(get_db),
) -> ErrorLogs:
    try:
        filter_obj = {}
        sort_obj = []
        range_obj = []

        if filter:
            filter_obj = json.loads(filter)
        if sort:
            sort_obj = json.loads(sort)
        if range:
            range_obj = json.loads(range)

        if filter_obj and "id" in filter_obj:
            if isinstance(filter_obj["id"], list):
                return get_error_by_list_ids(db, filter_obj["id"])
            return get_error(db, filter_obj["id"])

        return get_all_errors(db, sort=sort_obj, range=range_obj)
    except json.JSONDecodeError as ex:
        raise HTTPException(status_code=400, detail="error decoding filter, sort or range parameters") from ex


@router.put("/errors/{error_id}", summary="Update error")
async def update_error_endpoint(
    error_id: int, error_request: ErrorLogUpdateRequest, db: Session = Depends(get_db)
) -> SingleErrorLog:
    try:
        updated_errorLog = update_error(db, error_id, error_request)
        return {"data": updated_errorLog}
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
        raise HTTPException(status_code=400, detail="error updating error") from ex


@router.post("/errors", summary="Create error")
async def create_error_endpoint(error_request: ErrorLogCreateRequest, db: Session = Depends(get_db)) -> ErrorLog:
    try:
        return create_error(db, error_request)
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
        raise HTTPException(status_code=400, detail="error creating error") from ex


@router.delete("/errors/{error_id}", summary="Delete error")
async def delete_error_endpoint(error_id: int, db: Session = Depends(get_db)):
    error_deleted = delete_error(db, error_id)

    if error_deleted:
        return {"data": error_deleted}
    raise HTTPException(status_code=400, detail="error deleting dividend")
