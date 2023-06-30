from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from solarpark.persistence.database import get_db
from solarpark.persistence.generate import create_share_pdf
from solarpark.persistence.members import get_member
from solarpark.persistence.shares import get_shares_by_member

router = APIRouter()


@router.get("/generate/sharepdf/{member_id}", summary="Get pdf shares")
async def get_pdf_endpoint(member_id: int, db: Session = Depends(get_db)):
    member = get_member(db, member_id)
    if len(member) != 1:
        raise HTTPException(status_code=400, detail="member not found")

    shares = get_shares_by_member(db, member_id)
    if not len(shares["data"]) > 1:
        raise HTTPException(status_code=400, detail="no shares found for member")

    pdf = create_share_pdf(member["data"][0], shares["data"])
    headers = {"Content-Disposition": 'attachment; filename="andelsbevis.pdf"'}  # DOWNLOAD
    # headers = {"Content-Disposition": 'inline; filename="out.pdf"'}  # DISPLAY ONLY
    return Response(pdf, headers=headers, media_type="application/pdf")
