from email.message import EmailMessage


class LoopiaEmailClient:

    def __init__(self, email, password, smtp_server="mailcluster.loopia.se", port=587):
        self.email = email
        self.password = password
        self.smtp_server = smtp_server
        self.port = port

        self.mime_types = {
            ".pdf": ("application", "pdf"),
            ".png": ("image", "png"),
            ".jpg": ("image", "jpeg"),
            ".jpeg": ("image", "jpeg"),
        }

    def create_message(self, to, subject, body_html=None, body_text=None) -> EmailMessage:
        msg = EmailMessage()
        msg["From"] = self.email
        msg["To"] = to if isinstance(to, str) else ", ".join(to)
        msg["Subject"] = subject

        if body_html and body_text:
            msg.set_content(body_text)
            msg.add_alternative(body_html, subtype="html")
        elif body_html:
            msg.set_content(body_html, subtype="html")
        else:
            msg.set_content(body_text or "")

        return msg
