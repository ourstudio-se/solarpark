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
from solarpark.services import resend_client, sendgrid_client
from solarpark.services.resend import ResendEmailClient
from solarpark.services.sendgrid import SendGridClient
from solarpark.settings import settings

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

    if member.email is None:
        raise HTTPException(status_code=400, detail="member has no email")

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
        to_emails=[member.email],
        from_email=settings.SENDGRID_EMAIL_FROM,
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


def send_summary_with_resend(resend_client: ResendEmailClient):

    res = resend_client.send_email(
        to="simon@ourstudio.se",
        subject="Hello from Backend!",
        html="<p>This is a <strong>test email</strong> sent via Resend.</p>",
        text="This is a test email sent via Resend.",
    )
    a = 20
    print(res)


@router.post(
    "/email",
    summary="Test sending email",
    status_code=202,
)
async def send_summary_mail(
    member_id: int,
    resend: ResendEmailClient = Depends(resend_client),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):

    res = resend.send_email(
        to="simon@ourstudio.se",
        subject="Hello from Backend!",
        html="<p>This is a <strong>test email</strong> sent via Resend.</p>",
        text="This is a test email sent via Resend.",
    )
    a = 20
    print(res)
    background_tasks.add_task(send_summary_with_resend, resend, member_id)
