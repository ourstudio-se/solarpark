import io
import os
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from solarpark.api.generate import generate_certificate_pdf
from solarpark.models.email import Attachment, Email
from solarpark.persistence.database import get_db
from solarpark.persistence.members import get_member
from solarpark.persistence.shares import get_shares_by_member
from solarpark.services import sendgrid_client
from solarpark.services.sendgrid import SendGridClient

router = APIRouter()


def get_image_path():
    path = f"{os.getcwd()}/solarpark/templates/solarparkPDF.png"
    return path


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
        "title": "Andelsbevis Solar Park",
        "id": member.id,
        "name": f"{member.firstname} {member.lastname}" if member.lastname is not None else member.org_name,
        "shares": [{"id": share.id, "purchased_at": share.purchased_at.strftime("%Y-%m-%d")} for share in shares],
        "image_path": get_image_path(),
        "today": datetime.today().strftime("%Y-%m-%d"),
    }

    env = Environment(loader=FileSystemLoader("solarpark/templates/"))
    template_email = env.get_template("email.html")

    html_mail = template_email.render(context)
    pdf = generate_certificate_pdf(member, shares)

    mail = Email(
        subject="Andelsbevis Solar Park",
        to_emails=["joar@ourstudio.se", "simon@ourstudio.se"],  # Change
        from_email="joar@ourstudio.se",  # Change
        html_content=html_mail,
        attachments=[
            Attachment(file_content=io.BytesIO(pdf), file_name="andelsbevis.pdf", file_type="application/pdf")
        ],
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
