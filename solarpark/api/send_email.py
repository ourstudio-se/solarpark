import os
import time

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from structlog import get_logger

from solarpark.api.generate import generate_certificate_pdf
from solarpark.models.email import Attachment, Email
from solarpark.persistence.database import get_db
from solarpark.persistence.economics import get_economics_by_member
from solarpark.persistence.members import get_all_member_ids_and_emails, get_member
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
        get_logger().error(f"Failed to find member id {member_id}")
        raise HTTPException(status_code=404, detail="No member found")

    economics = get_economics_by_member(db, member_id)
    if len(economics["data"]) != 1:
        get_logger().error(f"Failed to find economics for member id {member_id}")
        raise HTTPException(status_code=404, detail="No economics found for member")

    shares = get_shares_by_member(db, member_id)
    if not len(shares["data"]) > 0:
        get_logger().error(f"Failed to find shares for member id {member_id}")
        raise HTTPException(status_code=404, detail="No shares found for member")

    member = members["data"][0]
    shares = shares["data"]
    economics = economics["data"][0]

    if member.email is None:
        get_logger().error(f"Member id {member_id} has no email address")
        raise HTTPException(status_code=400, detail="Member has no email address")

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


def send_bulk_summary_and_certificate_with_loopia(
    loopia: LoopiaEmailClient,
    db: Session,
):
    rate_limit_seconds = 20
    members = get_all_member_ids_and_emails(db)
    for member_id, email in members:
        if email is None or email == "":
            continue

        try:
            send_summary_and_certificate_with_loopia(loopia, db, member_id)
        except Exception as e:
            get_logger().error(f"Bulk run: not sending email for member {member_id}: {e}")

        time.sleep(rate_limit_seconds)


@router.post(
    "/email/certificate/{member_id}",
    summary="Summation and certificate of participation for member",
    status_code=202,
)
async def send_email_with_certificate(
    member_id: int,
    loopia: LoopiaEmailClient = Depends(loopia_client),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    background_tasks.add_task(send_summary_and_certificate_with_loopia, loopia, db, member_id)


@router.post(
    "/email/bulk",
    summary="Summation and certificate of participation for all members",
    status_code=202,
)
async def send_email_summation_bulk_run(
    loopia: LoopiaEmailClient = Depends(loopia_client),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    background_tasks.add_task(send_bulk_summary_and_certificate_with_loopia, loopia, db)
