import os
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from solarpark.api.generate import generate_certificate_pdf
from solarpark.models.eemail import Attachment, Email
from solarpark.persistence.database import get_db
from solarpark.persistence.economics import get_economics_by_member
from solarpark.persistence.members import get_member
from solarpark.persistence.shares import get_shares_by_member
from solarpark.services import loopia_client
from solarpark.services.loopia import LoopiaEmailClient

router = APIRouter()


def get_image_path():
    path = f"{os.getcwd()}/solarpark/templates/solarparkPDF.png"
    return path


def send_certificate_with_loopia(
    loopia: LoopiaEmailClient,
    db: Session,
    member_id: int,
):
    members = get_member(db, member_id)
    if len(members["data"]) != 1:
        raise HTTPException(status_code=400, detail="member not found")

    economics = get_economics_by_member(db, member_id)
    if not len(economics["data"]) > 0:
        raise HTTPException(status_code=400, detail="no economics found for member")

    shares = get_shares_by_member(db, member_id)
    if not len(shares["data"]) > 0:
        raise HTTPException(status_code=400, detail="no shares found for member")

    member = members["data"][0]
    shares = shares["data"]
    economics = economics["data"][0]

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
        to_email="simon@ourstudio.se",
        subject="Andelsbevis Solar Park",
        html_content=html_mail,
        attachments=[
            Attachment(file_content=pdf, file_name="andelsbevis.pdf", sub_type="pdf", main_type="application")
        ],
    )

    loopia.send(mail)


@router.post(
    "/email/certificate/{member_id}",
    summary="Summation and certificate of participation for member",
    status_code=202,
)
async def send_certificate(
    member_id: int,
    loopia: LoopiaEmailClient = Depends(loopia_client),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    background_tasks.add_task(send_certificate_with_loopia, loopia, db, member_id)
