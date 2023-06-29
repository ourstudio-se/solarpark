from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from solarpark.persistence.database import get_db
from solarpark.persistence.generate import create_share_pdf

router = APIRouter()


@router.get("/generate/sharepdf/{member_id}", summary="Get pdf shares")
async def get_pdf_endpoint(member_id: int, db: Session = Depends(get_db)):
    pdf = create_share_pdf(db, member_id)
    headers = {"Content-Disposition": 'attachment; filename="out.pdf"'}  # DOWNLOAD
    # headers = {"Content-Disposition": 'inline; filename="out.pdf"'}  # DISPLAY ONLY
    return Response(pdf, headers=headers, media_type="application/pdf")
