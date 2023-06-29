import pdfkit
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from solarpark.persistence.members import get_member
from solarpark.persistence.shares import get_shares_by_member


def create_share_pdf(db: Session, member_id: int):
    member = get_member(db, member_id)["data"][0]
    shares = get_shares_by_member(db, member_id)["data"]

    context = {
        "title": "Test Solarpark",
        "id": member_id,
        "name": f"{member.firstname} {member.lastname}",
        "shares": [{"id": share.id} for share in shares],
    }

    env = Environment(loader=FileSystemLoader("solarpark/templates/"))
    template = env.get_template("pdf.html")  # sharepdf.html
    html = template.render(context)
    pdf = pdfkit.from_string(input=html, options={"enable-local-file-access": ""})

    return pdf
