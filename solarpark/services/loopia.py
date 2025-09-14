# pylint: disable=E0611
import smtplib
from email.message import EmailMessage

from structlog import get_logger

from solarpark.models.email import Email
from solarpark.settings import settings


class LoopiaEmailClient:
    def __init__(self):
        self.email = settings.LOOPIA_EMAIL_FROM
        self.password = settings.LOOPIA_PASSWORD
        self.smtp_server = settings.LOOPIA_SMTP_SERVER
        self.port = settings.LOOPIA_PORT

    def send(self, email: Email):
        if settings.MAIL_TEST_MODE:
            get_logger().info(f"Test mode enabled, email not sent to {email.to_email} subject {email.subject}")
            return

        msg = EmailMessage()
        msg["From"] = self.email
        msg["To"] = email.to_email
        msg["Subject"] = email.subject
        msg.set_content(email.html_content, subtype="html")
        if email.attachments:
            for attachment in email.attachments:
                msg.add_attachment(
                    attachment.file_content,
                    maintype=attachment.main_type,
                    subtype=attachment.sub_type,
                    filename=attachment.file_name,
                )

        try:
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.email, self.password)
                server.send_message(msg)

            get_logger().info(f"Email sent successfully to {email.to_email} subject {email.subject}")
        except Exception as e:
            get_logger().error(f"Failed to send email to {email.to_email} subject {email.subject} err {str(e)}")
