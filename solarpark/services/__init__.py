from solarpark.services.sendgrid import SendGridClient


def sendgrid_client() -> SendGridClient:
    return SendGridClient()
