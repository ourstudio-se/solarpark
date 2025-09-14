import os

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from solarpark.api.generate import generate_certificate_pdf
from solarpark.models.email import Attachment, Email
from solarpark.persistence.database import get_db
from solarpark.persistence.economics import get_economics_by_member
from solarpark.persistence.members import get_member
from solarpark.persistence.shares import get_shares_by_member
from solarpark.services import loopia_client
from solarpark.services.loopia import LoopiaEmailClient

router = APIRouter()


def sek(value) -> str:
    try:
        return f"{float(value):,.0f} kr".replace(",", " ")
    except (TypeError, ValueError):
        return "–"


def get_image_path():
    path = f"{os.getcwd()}/solarpark/templates/solarparkPDF.png"
    return path


def send_summary_and_certificate_with_loopia(
    loopia: LoopiaEmailClient,
    db: Session,
    member_id: int,
):
    members = get_member(db, member_id)
    if len(members["data"]) != 1:
        raise HTTPException(status_code=400, detail="member not found")

    economics = get_economics_by_member(db, member_id)
    if len(economics["data"]) != 1:
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
        "title": "Solar Park",
        "id": member.id,
        "name": f"{member.firstname} {member.lastname}" if member.lastname is not None else member.org_name,
        "economics": {
            "nr_of_shares": economics.nr_of_shares,
            "total_investment": economics.total_investment,
            "current_value": economics.current_value,
            "reinvested": economics.reinvested,
            "account_balance": economics.account_balance,
            "pay_out": bool(economics.pay_out),
            "disbursed": economics.disbursed,
            "last_dividend_year": economics.last_dividend_year,
            "issued_dividend": economics.issued_dividend,
        },
        "image_path": get_image_path(),
    }

    env = Environment(loader=FileSystemLoader("solarpark/templates/"))
    template_email = env.get_template("summary_email.html")

    env.filters["sek"] = sek

    html_mail = template_email.render(context)
    pdf = generate_certificate_pdf(member, shares)

    mail = Email(
        to_email=member.email,
        subject="Summering av ditt medlemskap i Solar Park",
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
    background_tasks.add_task(send_summary_and_certificate_with_loopia, loopia, db, member_id)
