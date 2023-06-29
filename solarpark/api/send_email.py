from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from solarpark.persistence.database import get_db
from solarpark.persistence.send_email import send_email

router = APIRouter()


@router.get("/email/pdf/{member_id}", summary="Text + attach pdf")
async def send_email_endpoint(
    member_id: int,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> JSONResponse:
    send_email(db, member_id, background_tasks)

    return JSONResponse(status_code=200, content={"message": "email has been sent"})
