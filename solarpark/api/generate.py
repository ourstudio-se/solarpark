import pdfkit
from fastapi import APIRouter, Depends, HTTPException, Response
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from solarpark.persistence.database import get_db
from solarpark.persistence.members import get_member
from solarpark.persistence.shares import get_shares_by_member

router = APIRouter()


def generate_certificate_pdf(member, shares):
    context = {
        "title": "Test Solarpark",
        "id": member.id,
        "name": f"{member.firstname} {member.lastname}",
        "shares": [{"id": share.id} for share in shares],
    }

    env = Environment(loader=FileSystemLoader("solarpark/templates/"))
    template = env.get_template("pdf.html")

    html_pdf = template.render(context)

    # Check if wkhtmltopdf is on OS path, else fallback to "/bin/wkhtmltopdf" for production setup
    pdf = None
    config = None
    try:
        config = pdfkit.configuration()
        pdf = pdfkit.from_string(
            input=html_pdf,
            options={"enable-local-file-access": ""},
            configuration=config,
        )
    except OSError:
        config = pdfkit.configuration(wkhtmltopdf="/bin/wkhtmltopdf")
        pdf = pdfkit.from_string(
            input=html_pdf,
            options={"enable-local-file-access": ""},
            configuration=config,
        )

    return pdf


@router.get("/generate/certificate/{member_id}", summary="Generate participation certificate")
async def generate_certificate_endpoint(member_id: int, db: Session = Depends(get_db)):
    member = get_member(db, member_id)
    if len(member["data"]) != 1:
        raise HTTPException(status_code=400, detail="member not found")

    shares = get_shares_by_member(db, member_id)
    if not len(shares["data"]) > 0:
        raise HTTPException(status_code=400, detail="no shares found for member")

    pdf = generate_certificate_pdf(member["data"][0], shares["data"])

    headers = {"Content-Disposition": 'attachment; filename="certifikat.pdf"'}  # DOWNLOAD
    # pylint: disable = W0105
    """ headers = {
        "Content-Disposition": 'inline; filename="certifikat.pdf"'
    } """  # DISPLAY ONLY

    return Response(pdf, headers=headers, media_type="application/pdf")
