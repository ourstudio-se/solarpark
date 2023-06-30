import base64

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Attachment, Disposition, FileContent, FileName, FileType, Mail
from structlog import get_logger

from solarpark.models.email import Email
from solarpark.settings import settings


class SendGridClient:
    def __init__(self):
        self._api_key = settings.SENDGRID_API_KEY
        self._client = SendGridAPIClient(self._api_key)

    def send(self, mail: Email):
        message = Mail(
            from_email=mail.from_email,
            to_emails=mail.to_email,
            subject=mail.subject,
            html_content=mail.html_content,
        )

        if mail.attachments:
            attachments = []
            for attachment in mail.attachments:
                attachments.append(
                    Attachment(
                        file_content=FileContent(base64.b64encode(attachment.file_content.getvalue()).decode()),
                        file_name=FileName(attachment.file_name),
                        file_type=FileType(attachment.file_type),
                        disposition=Disposition("attachment"),
                    )
                )
            message.attachment = attachments
        try:
            self._client.send(message)
        except Exception as ex:
            get_logger().error(ex)
