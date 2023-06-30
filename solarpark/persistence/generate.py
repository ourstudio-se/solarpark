import pdfkit
from jinja2 import Environment, FileSystemLoader


def create_share_pdf(member, shares):
    context = {
        "title": "Test Solarpark",
        "id": member.id,
        "name": f"{member.firstname} {member.lastname}",
        "shares": [{"id": share.id} for share in shares],
    }

    env = Environment(loader=FileSystemLoader("solarpark/templates/"))
    template = env.get_template("pdf.html")  # sharepdf.html
    html = template.render(context)
    config = pdfkit.configuration(wkhtmltopdf="/bin/wkhtmltopdf")
    pdf = pdfkit.from_string(input=html, options={"enable-local-file-access": ""}, configuration=config)

    return pdf
