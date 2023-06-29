# pylint: disable=R0914, R1711
import io

import pdfkit
from fastapi import BackgroundTasks, UploadFile
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader

from solarpark.persistence.members import get_member
from solarpark.persistence.shares import get_shares_by_member
from solarpark.settings import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER="solarpark/templates",
)


def send_email(
    db,
    member_id,
    background_tasks: BackgroundTasks,
):
    member = get_member(db, member_id)["data"][0]
    shares = get_shares_by_member(db, member_id)["data"]
    subject = "Solarpark ägande (test)"
    email_to = settings.MAIL_FROM  # ÄNDRA VID DEPLOY

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

    pdf = io.BytesIO(
        pdfkit.from_string(
            input=html_pdf,
            options={
                "enable-local-file-access": "",
            },
        )
    )
    upload_pdf = UploadFile(
        filename="summering.pdf",
        file=pdf,
    )
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=html_mail,
        subtype=MessageType.html,
        attachments=[upload_pdf],
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)

    return None
