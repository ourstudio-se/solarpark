# from solarpark.services.resend import ResendEmailClient
from solarpark.services.sendgrid import SendGridClient


def sendgrid_client() -> SendGridClient:
    return SendGridClient()


# def resend_client() -> ResendEmailClient:
#     return ResendEmailClient()
