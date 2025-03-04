from typing import Dict, List, Optional

import resend

from solarpark.settings import settings


class ResendEmailClient:
    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY

    def send_email(
        self,
        to: str | List[str],
        subject: str,
        html: Optional[str] = None,
        text: Optional[str] = None,
        from_email: str = settings.RESEND_EMAIL_FROM,
        attachments: Optional[List[Dict]] = None,
    ):
        """
        Send an email with multiple configuration options

        Args:
            to: Recipient email address(es)
            subject: Email subject line
            html: HTML content of the email
            text: Plain text content of the email
            from_email: Sender's email address
            reply_to: Reply-to email address
            cc: Carbon copy recipients
            bcc: Blind carbon copy recipients
            attachments: List of attachment dictionaries

        Returns:
            Dict: Resend API response
        """
        try:
            params = {
                "from": from_email,
                "to": to,
                "subject": subject,
            }

            if html:
                params["html"] = html
            if text:
                params["text"] = text
            if attachments:
                params["attachments"] = attachments

            return resend.Emails.send(params)

        except Exception as e:
            print(f"Email sending failed: {e}")
            return None

    def batch_send(self, emails: List[Dict[str, str]], from_email: str = "your-verified-sender@example.com"):
        """
        Send multiple emails in a batch

        Args:
            emails: List of email configurations
            from_email: Default sender email

        Returns:
            List of sending results
        """
        results = []
        for email_config in emails:
            config = {"from": from_email, **email_config}
            try:
                result = resend.Emails.send(config)
                results.append(result)
            except Exception as e:
                print(f"Failed to send email: {e}")
                results.append(None)

        return results


# Example usage
# def main():
#     # Replace with your actual Resend API key


#     # Create email client
#     email_client = ResendEmailClient()

#     # Single email send
#     single_result = email_client.send_email(
#         to="recipient@example.com",
#         subject="Hello from Resend!",
#         html="<p>This is a <strong>test email</strong> sent via Resend.</p>",
#         text="This is a test email sent via Resend."
#     )

#     # Batch email send
#     batch_emails = [
#         {
#             "to": "user1@example.com",
#             "subject": "Batch Email 1",
#             "html": "<p>First batch email</p>"
#         },
#         {
#             "to": "user2@example.com",
#             "subject": "Batch Email 2",
#             "html": "<p>Second batch email</p>"
#         }
#     ]

#     batch_results = email_client.batch_send(batch_emails)

# if __name__ == "__main__":
#     main()
