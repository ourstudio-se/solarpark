import io

import pdfkit
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from solarpark.models.email import Attachment, Email
from solarpark.persistence.database import get_db
from solarpark.persistence.members import get_member
from solarpark.persistence.shares import get_shares_by_member
from solarpark.services import sendgrid_client
from solarpark.services.sendgrid import SendGridClient

router = APIRouter()


def send_certificate_with_sendgrid(
    sendgrid: SendGridClient,
    db: Session,
    member_id: int,
):
    members = get_member(db, member_id)
    if len(members["data"]) != 1:
        raise HTTPException(status_code=400, detail="member not found")

    shares = get_shares_by_member(db, member_id)
    if not len(shares["data"]) > 0:
        raise HTTPException(status_code=400, detail="no shares found for member")

    member = members["data"][0]
    shares = shares["data"]

    context = {
        "title": "Test Solarpark",
        "id": member_id,
        "name": f"{member.firstname} {member.lastname}",
        "shares": [{"id": share.id} for share in shares],
    }

    env = Environment(loader=FileSystemLoader("solarpark/templates/"))
    template_email = env.get_template("email.html")
    template_pdf = env.get_template("pdf.html")

    html_pdf = template_pdf.render(context)
    html_mail = template_email.render(context)

    # Check if wkhtmltopdf is on OS path, else fallback to "/bin/wkhtmltopdf" for production setup
    pdf = None
    config = None
    try:
        config = pdfkit.configuration()
        pdf = io.BytesIO(
            pdfkit.from_string(
                input=html_pdf,
                options={
                    "enable-local-file-access": "",
                },
                configuration=config,
            )
        )
    except OSError:
        config = pdfkit.configuration(wkhtmltopdf="/bin/wkhtmltopdf")
        pdf = io.BytesIO(
            pdfkit.from_string(
                input=html_pdf,
                options={
                    "enable-local-file-access": "",
                },
                configuration=config,
            )
        )

    mail = Email(
        subject="Solarpark ägande (test)",
        to_email="simon@ourstudio.se",  # Change
        from_email="joar@ourstudio.se",  # Change
        html_content=html_mail,
        attachments=[Attachment(file_content=pdf, file_name="summering.pdf", file_type="application/pdf")],
    )

    sendgrid.send(mail)


@router.post(
    "/email/certificate/{member_id}",
    summary="Summation and certificate of participation for member",
    status_code=202,
)
async def send_certificate(
    member_id: int,
    sendgrid: SendGridClient = Depends(sendgrid_client),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    background_tasks.add_task(send_certificate_with_sendgrid, sendgrid, db, member_id)
